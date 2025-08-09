export default async function handler(req, res) {
  const { token, repo } = req.query;
  let installUrl = null;
  if (token && repo) {
    const response = await fetch(`https://api.github.com/repos/${repo}/installation`, {
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: 'application/vnd.github+json'
      }
    });
    if (response.status === 404) {
      installUrl = `https://github.com/apps/${process.env.GITHUB_APP_SLUG}/installations/new`;
    }
  }
  res.status(200).json({ install_url: installUrl });
}
