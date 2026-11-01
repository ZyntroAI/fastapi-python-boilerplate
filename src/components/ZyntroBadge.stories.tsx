import type { Meta, StoryObj } from '@storybook/react';
import { ZyntroBadge } from './ZyntroBadge';

const meta: Meta<typeof ZyntroBadge> = {
  title: 'Components/Badge',
  component: ZyntroBadge,
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'success', 'warning', 'danger', 'info', 'neon']
    },
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg']
    }
  },
  parameters: {
    chromatic: { pauseAnimationAtEnd: true }
  }
};

export default meta;
type Story = StoryObj<typeof ZyntroBadge>;

export const Default: Story = {
  args: { children: 'Badge Text' }
};

export const AllVariants: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
      <ZyntroBadge variant="default">Default</ZyntroBadge>
      <ZyntroBadge variant="success">Success</ZyntroBadge>
      <ZyntroBadge variant="warning">Warning</ZyntroBadge>
      <ZyntroBadge variant="danger">Danger</ZyntroBadge>
      <ZyntroBadge variant="info">Info</ZyntroBadge>
      <ZyntroBadge variant="neon">Neon</ZyntroBadge>
    </div>
  )
};

export const AllSizes: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
      <ZyntroBadge size="sm">Small</ZyntroBadge>
      <ZyntroBadge size="md">Medium</ZyntroBadge>
      <ZyntroBadge size="lg">Large</ZyntroBadge>
    </div>
  )
};

export const DarkMode: Story = {
  parameters: { darkMode: { current: 'dark' } },
  render: AllVariants.render
};
