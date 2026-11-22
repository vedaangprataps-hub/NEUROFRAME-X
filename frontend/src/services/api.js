export const uploadVideo = async (file, onUploadProgress) => {
  const formData = new FormData();
  formData.append('file', file);

  // Use fetch for simplicity; onUploadProgress is ignored (no native support).
  const response = await fetch('/process', {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Upload failed with status ${response.status}`);
  }
  return await response.json();
};
