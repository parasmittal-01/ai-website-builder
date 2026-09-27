import { fireEvent, render, screen } from '@testing-library/react';
import { generateProject } from './api';
import App from './App';

jest.mock('./api', () => ({
  generateProject: jest.fn(),
  getPreviewUrl: (projectId) => `http://127.0.0.1:8000/generated_projects/${projectId}/index_preview.html`,
  getDownloadUrl: (projectId) => `http://127.0.0.1:8000/download/${projectId}.zip`,
}));

test('renders the website builder and prompt starters', () => {
  render(<App />);
  expect(screen.getByRole('heading', { name: /make a site that feels like you/i })).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /Make my website/i })).toBeDisabled();
  expect(screen.getByLabelText(/your website idea/i)).toBeInTheDocument();

  fireEvent.click(screen.getByRole('button', { name: /cozy neighborhood coffee shop/i }));

  expect(screen.getByLabelText(/your website idea/i)).toHaveValue('A cozy neighborhood coffee shop');
  expect(screen.getByRole('button', { name: /Make my website/i })).toBeEnabled();
});

test('shows the generated preview and download action', async () => {
  generateProject.mockResolvedValue({ project_id: 'project-123' });
  render(<App />);

  fireEvent.change(screen.getByLabelText(/your website idea/i), {
    target: { value: 'A website for my bookshop' },
  });
  fireEvent.click(screen.getByRole('button', { name: /Make my website/i }));

  expect(await screen.findByTitle('Generated website preview')).toHaveAttribute(
    'src',
    'http://127.0.0.1:8000/generated_projects/project-123/index_preview.html',
  );
  expect(screen.getByRole('link', { name: /Download files/i })).toHaveAttribute(
    'href',
    'http://127.0.0.1:8000/download/project-123.zip',
  );
  expect(generateProject).toHaveBeenCalledWith('A website for my bookshop');
});

test('shows errors returned by the generation API', async () => {
  jest.spyOn(console, 'error').mockImplementation(() => {});
  generateProject.mockRejectedValue({
    response: { data: { error: 'Gemini is temporarily unavailable' } },
  });
  render(<App />);

  fireEvent.change(screen.getByLabelText(/your website idea/i), {
    target: { value: 'A website for my bookshop' },
  });
  fireEvent.click(screen.getByRole('button', { name: /Make my website/i }));

  expect(await screen.findByRole('alert')).toHaveTextContent('Gemini is temporarily unavailable');
});
