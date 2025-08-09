export default async function handler(req, res) {
  const client_id = process.env.GITHUB_CLIENT_ID;
  const response = await fetch('https://github.com/login/device/code', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    },
    body: JSON.stringify({
      client_id,
      scope: 'repo'
    })
  });
  const data = await response.json();
  res.status(200).json(data);
}
