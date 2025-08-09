import { useState } from 'react';

export default function Home() {
  const [verification, setVerification] = useState(null);
  const [installUrl, setInstallUrl] = useState('');

  const login = async () => {
    const res = await fetch('/api/auth/device');
    const data = await res.json();
    setVerification(data);

    const tokenRes = await fetch('/api/auth/token?device_code=' + data.device_code);
    const tokenData = await tokenRes.json();

    const repo = 'sample/repo';
    const instRes = await fetch('/api/installations?token=' + tokenData.access_token + '&repo=' + encodeURIComponent(repo));
    const instData = await instRes.json();
    if (instData.install_url) {
      setInstallUrl(instData.install_url);
    }
  };

  return (
    <div>
      <button onClick={login}>Login with GitHub</button>
      {verification && (
        <p>
          Visit <a href={verification.verification_uri} target="_blank" rel="noreferrer">{verification.verification_uri}</a> and enter code {verification.user_code}
        </p>
      )}
      {installUrl && (
        <p>
          Install app: <a href={installUrl} target="_blank" rel="noreferrer">{installUrl}</a>
        </p>
      )}
    </div>
  );
}
