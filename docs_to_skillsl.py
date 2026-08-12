#!/usr/bin/env python3
"""
docs_to_skill.py
Convert documentation pages (Microsoft Learn, GitHub Docs, etc.) 
into structured skill files for agent systems.
"""

import re
import json
import argparse
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional, List

try:
    import requests
    from bs4 import BeautifulSoup, NavigableString
except ImportError:
    raise ImportError("Install dependencies: pip install requests beautifulsoup4")


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class SkillConfig:
    """Configuration for skill generation."""
    repo_owner: str = "zyntroai"
    repo_name: str = "new-crystalcastle"
    default_path: str = "docs/skills"
    attribution_footer: bool = True
    include_images: bool = True
    max_image_size_kb: int = 500
    language: str = "en"
    
    @property
    def full_repo(self) -> str:
        return f"{self.repo_owner}/{self.repo_name}"


# =============================================================================
# HTML TO MARKDOWN CONVERTER
# =============================================================================

class HtmlToMarkdown:
    """Convert HTML documentation to clean Markdown."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.image_count = 0
        
    def convert(self, html: str) -> str:
        """Convert HTML string to Markdown."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script/style/nav/footer elements
        for tag in soup.find_all(['script', 'style', 'nav', 'footer', 
                                   'aside', 'header', '.breadcrumb']):
            tag.decompose()
        
        # Convert main content
        body = soup.find('main') or soup.find('article') or soup.find('body') or soup
        return self._process_element(body)
    
    def _process_element(self, element) -> str:
        """Recursively process HTML elements."""
        if isinstance(element, NavigableString):
            return str(element)
        
        tag_name = element.name
        if not tag_name:
            return ''.join(self._process_element(child) for child in element.children)
        
        handlers = {
            'h1': self._heading,
            'h2': self._heading,
            'h3': self._heading,
            'h4': self._heading,
            'h5': self._heading,
            'h6': self._heading,
            'p': self._paragraph,
            'pre': self._code_block,
            'code': self._inline_code,
            'ul': self._list,
            'ol': self._ordered_list,
            'li': self._list_item,
            'a': self._link,
            'img': self._image,
            'table': self._table,
            'tr': self._table_row,
            'td': self._table_cell,
            'th': self._table_header,
            'blockquote': self._blockquote,
            'strong': self._bold,
            'b': self._bold,
            'em': self._italic,
            'i': self._italic,
            'br': lambda e: '\n',
            'hr': lambda e: '\n---\n',
            'div': self._generic,
            'span': self._generic,
        }
        
        handler = handlers.get(tag_name, self._generic)
        return handler(element)
    
    def _heading(self, element) -> str:
        level = int(element.name[1])
        text = self._get_text(element).strip()
        return f"\n{'#' * level} {text}\n"
    
    def _paragraph(self, element) -> str:
        text = self._get_text(element).strip()
        return f"\n{text}\n" if text else ""
    
    def _code_block(self, element) -> str:
        # Try to detect language
        lang = ''
        code_elem = element.find('code')
        if code_elem:
            classes = code_elem.get('class', [])
            for cls in classes:
                if cls.startswith('lang-') or cls.startswith('language-'):
                    lang = cls.split('-', 1)[1]
                    break
        
        # Get code content
        code = self._get_raw_text(element)
        # Clean up
        code = code.replace('\r\n', '\n').strip()
        
        return f"\n```{lang}\n{code}\n```\n"
    
    def _inline_code(self, element) -> str:
        text = self._get_text(element)
        return f"`{text}`"
    
    def _list(self, element) -> str:
        items = []
        for li in element.find_all('li', recursive=False):
            text = self._process_element(li).strip()
            text = re.sub(r'^\s*[\-\*]\s*', '', text)  # Remove existing bullets
            items.append(f"- {text}")
        return '\n' + '\n'.join(items) + '\n'
    
    def _ordered_list(self, element) -> str:
        items = []
        for i, li in enumerate(element.find_all('li', recursive=False), 1):
            text = self._process_element(li).strip()
            text = re.sub(r'^\s*\d+\.\s*', '', text)  # Remove existing numbers
            items.append(f"{i}. {text}")
        return '\n' + '\n'.join(items) + '\n'
    
    def _list_item(self, element) -> str:
        return self._get_text(element)
    
    def _link(self, element) -> str:
        href = element.get('href', '')
        text = self._get_text(element)
        
        # Resolve relative URLs
        if href and not href.startswith(('http://', 'https://', '#', 'mailto:')):
            from urllib.parse import urljoin
            href = urljoin(self.base_url, href)
        
        return f"[{text}]({href})"
    
    def _image(self, element) -> str:
        src = element.get('src', '')
        alt = element.get('alt', 'image')
        
        if not src:
            return ""
        
        # Resolve relative URLs
        if not src.startswith(('http://', 'https://')):
            from urllib.parse import urljoin
            src = urljoin(self.base_url, src)
        
        self.image_count += 1
        
        # For large images, link to source instead of embedding
        return f"\n![{alt}]({src})\n"
    
    def _table(self, element) -> str:
        rows = []
        for child in element.children:
            if child.name in ('tr',):
                rows.append(self._process_element(child))
        
        if not rows:
            return ""
        
        # Add separator after header
        header = rows[0] if rows else ""
        separator = "|" + "|".join(["---"] * header.count("|")) + "|"
        
        result = "\n" + "\n".join(rows[:1])
        if len(rows) > 1:
            result += "\n" + separator + "\n" + "\n".join(rows[1:])
        
        return result + "\n"
    
    def _table_row(self, element) -> str:
        cells = []
        for child in element.children:
            if child.name in ('td', 'th'):
                cells.append(self._process_element(child).strip())
        return "| " + " | ".join(cells) + " |"
    
    def _table_cell(self, element) -> str:
        return self._get_text(element)
    
    def _table_header(self, element) -> str:
        return self._get_text(element)
    
    def _blockquote(self, element) -> str:
        text = self._get_text(element).strip()
        lines = text.split('\n')
        return '\n' + '\n'.join(f"> {line}" for line in lines) + '\n'
    
    def _bold(self, element) -> str:
        return f"**{self._get_text(element)}**"
    
    def _italic(self, element) -> str:
        return f"*{self._get_text(element)}*"
    
    def _generic(self, element) -> str:
        return ''.join(self._process_element(child) for child in element.children)
    
    def _get_text(self, element) -> str:
        """Get clean text from element."""
        text = ''.join(self._process_element(child) for child in element.children)
        # Clean up whitespace
        text = re.sub(r'\n\s*\n', '\n', text)
        text = re.sub(r' +', ' ', text)
        return text.strip()
    
    def _get_raw_text(self, element) -> str:
        """Get raw text without markdown processing."""
        texts = []
        for descendant in element.descendants:
            if isinstance(descendant, NavigableString):
                texts.append(str(descendant))
        return ''.join(texts)


# =============================================================================
# SKILL GENERATOR
# =============================================================================

class SkillGenerator:
    """Generate skill files from documentation."""
    
    def __init__(self, config: SkillConfig):
        self.config = config
        self.converter = None
        
    def fetch_and_convert(self, url: str) -> dict:
        """
        Fetch documentation page and convert to skill data.
        
        Returns dict with:
            - title
            - description  
            - content (markdown)
            - source_url
            - fetched_at
            - metadata
        """
        print(f"🔍 Fetching: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        self.converter = HtmlToMarkdown(url)
        markdown = self.converter.convert(response.text)
        
        # Extract title
        soup = BeautifulSoup(response.text, 'html.parser')
        title_tag = soup.find('h1') or soup.find('title')
        title = title_tag.get_text().strip() if title_tag else "Untitled"
        
        # Extract description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc['content'] if meta_desc and meta_desc.get('content') else ""
        
        # Clean up markdown
        markdown = self._clean_markdown(markdown)
        
        return {
            'title': title,
            'description': description,
            'content': markdown,
            'source_url': url,
            'fetched_at': datetime.utcnow().isoformat() + 'Z',
            'image_count': self.converter.image_count,
            'metadata': {
                'language': self.config.language,
                'platform': self._detect_platform(title, markdown),
            }
        }
    
    def _clean_markdown(self, markdown: str) -> str:
        """Clean up generated markdown."""
        # Remove excessive blank lines
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)
        # Fix code block issues
        markdown = re.sub(r'```\n\n+```', '```\n\n```', markdown)
        # Trim
        return markdown.strip()
    
    def _detect_platform(self, title: str, content: str) -> str:
        """Detect target platform from content."""
        text = (title + " " + content).lower()
        if 'windows' in text and 'linux' not in text and 'macos' not in text:
            return 'windows'
        if 'linux' in text or 'macos' in text or 'unix' in text:
            if 'windows' in text:
                return 'cross-platform'
            return 'unix'
        return 'cross-platform'
    
    def generate_skill_file(self, data: dict, output_path: Optional[str] = None) -> str:
        """
        Generate final skill markdown file.
        
        Returns the file content as string.
        """
        # Determine filename
        safe_title = re.sub(r'[^\w\s-]', '', data['title']).strip()
        safe_title = re.sub(r'[-\s]+', '-', safe_title).lower()
        
        if not output_path:
            output_path = f"{self.config.default_path}/{safe_title}.md"
        
        # Build skill content
        lines = [
            f"<!--",
            f"  Skill: {data['title']}",
            f"  Source: {data['source_url']}",
            f"  Fetched: {data['fetched_at']}",
            f"  Generated by: docs_to_skill.py",
            f"  Repository: {self.config.full_repo}",
            f"-->",
            "",
            f"# {data['title']}",
            "",
        ]
        
        if data['description']:
            lines.extend([
                f"> {data['description']}",
                "",
            ])
        
        lines.extend([
            "## Overview",
            "",
            f"- **Source**: [{data['source_url']}]({data['source_url']})",
            f"- **Platform**: {data['metadata']['platform']}",
            f"- **Language**: {data['metadata']['language']}",
            "",
            "---",
            "",
            data['content'],
            "",
        ])
        
        # Add attribution footer
        if self.config.attribution_footer:
            lines.extend([
                "---",
                "",
                "## Attribution",
                "",
                f"This skill was auto-generated from Microsoft Learn documentation.",
                f"",
                f"- **Original Source**: [{data['source_url']}]({data['source_url']})",
                f"- **Fetched**: {data['fetched_at']}",
                f"- **License**: Content subject to original source licensing terms",
                f"",
                f"> ⚠️ **Note**: This is a converted reference. Always verify against the",
                f"> latest official documentation before use in production.",
                "",
            ])
        
        return '\n'.join(lines)
    
    def save(self, content: str, filepath: str) -> Path:
        """Save skill file to disk."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"💾 Saved: {path}")
        print(f"📄 Size: {len(content):,} bytes")
        return path


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Convert documentation to skill files"
    )
    parser.add_argument('url', help='Documentation URL to convert')
    parser.add_argument('-o', '--output', help='Output file path')
    parser.add_argument('--repo', default='zyntroai/new-crystalcastle',
                        help='Target repository (owner/name)')
    parser.add_argument('--no-attribution', action='store_true',
                        help='Skip attribution footer')
    parser.add_argument('--no-images', action='store_true',
                        help='Skip image references')
    
    args = parser.parse_args()
    
    # Parse repo
    owner, name = args.repo.split('/', 1) if '/' in args.repo else ('', args.repo)
    
    config = SkillConfig(
        repo_owner=owner,
        repo_name=name,
        attribution_footer=not args.no_attribution,
        include_images=not args.no_images,
    )
    
    generator = SkillGenerator(config)
    
    try:
        # Fetch and convert
        data = generator.fetch_and_convert(args.url)
        
        # Generate skill file
        skill_content = generator.generate_skill_file(data, args.output)
        
        # Determine output path
        if args.output:
            output_path = args.output
        else:
            safe_title = re.sub(r'[^\w\s-]', '', data['title']).strip()
            safe_title = re.sub(r'[-\s]+', '-', safe_title).lower()
            output_path = f"docs/skills/{safe_title}.md"
        
        # Save
        saved_path = generator.save(skill_content, output_path)
        
        print(f"\n✅ Skill generated successfully!")
        print(f"   File: {saved_path}")
        print(f"   Title: {data['title']}")
        print(f"   Images: {data['image_count']}")
        
    except requests.RequestException as e:
        print(f"❌ Failed to fetch URL: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
