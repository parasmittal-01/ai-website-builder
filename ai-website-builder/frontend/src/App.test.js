import { render, screen } from '@testing-library/react';
import App from './App';

jest.mock('./api', () => ({
  generateProject: jest.fn(),
}));

test('renders the project generator', () => {
  render(<App />);
  expect(screen.getByRole('heading', { name: /AI Project Orchestrator/i })).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /Generate Project/i })).toBeInTheDocument();
  expect(screen.getByPlaceholderText(/Describe your project idea/i)).toBeInTheDocument();
});
