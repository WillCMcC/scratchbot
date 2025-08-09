export default async function handler(req, res) {
  const { device_code } = req.query;
  const client_id = process.env.GITHUB_CLIENT_ID;
  const response = await fetch('https://github.com/login/oauth/access_token', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    },
    body: JSON.stringify({
      client_id,
      device_code,
      grant_type: 'urn:ietf:params:oauth:grant-type:device_code'
    })
  });
  const data = await response.json();
  res.status(200).json(data);
}
