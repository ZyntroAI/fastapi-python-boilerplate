import type { Meta, StoryObj } from '@storybook/react';
import { ZyntroCard } from './ZyntroCard';
import { ZyntroButton } from './ZyntroButton';

const meta: Meta<typeof ZyntroCard> = {
  title: 'Components/Card',
  component: ZyntroCard,
  tags: ['autodocs'],
  argTypes: {
    variant: { control: 'select', options: ['default', 'elevated', 'outlined', 'glass'] }
  }
};

export default meta;
type Story = StoryObj<typeof ZyntroCard>;

export const Default: Story = {
  args: {
    children: <p>Card content goes here.</p>
  }
};

export const AllVariants: Story = {
  render: () => (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1.5rem' }}>
      <ZyntroCard variant="default">
        <h3 className="font-semibold mb-2">Default</h3>
        <p className="text-sm text-gray-500">Standard card style</p>
      </ZyntroCard>
      <ZyntroCard variant="elevated">
        <h3 className="font-semibold mb-2">Elevated</h3>
        <p className="text-sm text-gray-500">With shadow depth</p>
      </ZyntroCard>
      <ZyntroCard variant="outlined">
        <h3 className="font-semibold mb-2">Outlined</h3>
        <p className="text-sm text-gray-500">Border-only style</p>
      </ZyntroCard>
      <ZyntroCard variant="glass">
        <h3 className="font-semibold mb-2">Glass</h3>
        <p className="text-sm text-gray-500">Frosted glass effect</p>
      </ZyntroCard>
    </div>
  )
};

export const Interactive: Story = {
  render: () => (
    <ZyntroCard variant="elevated" onClick={() => alert('Clicked!')}>
      <h3 className="font-semibold mb-3">Interactive Card</h3>
      <p className="mb-4 text-sm text-gray-500">Click anywhere on this card</p>
      <ZyntroButton variant="primary">Action</ZyntroButton>
    </ZyntroCard>
  )
};

export const DarkMode: Story = {
  parameters: { darkMode: { current: 'dark' } },
  render: AllVariants.render
};
