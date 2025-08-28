const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
export async function tts(text) {
  const res = await fetch(`${BASE_URL}/api/v1/tts`, {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({ text })
  });
  return res.json();
}
