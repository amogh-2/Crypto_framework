document.addEventListener('DOMContentLoaded', () => {
  const encryptFileInput = document.getElementById('encryptFileInput');
  const encryptButton = document.getElementById('encryptButton');
  const encryptionDetails = document.getElementById('encryption-details');
  const downloadLink = document.getElementById('download-link');

  const decryptFileInput = document.getElementById('decryptFileInput');
  const decryptKey = document.getElementById('decryptKey');
  const decryptNonce = document.getElementById('decryptNonce');
  const decryptButton = document.getElementById('decryptButton');
  const decryptionDetails = document.getElementById('decryption-details');
  const decryptDownloadLink = document.getElementById('decrypt-download-link');

  encryptButton.addEventListener('click', () => {
      const file = encryptFileInput.files[0];
      if (!file) {
          alert('Please select a file to encrypt');
          return;
      }

      const formData = new FormData();
      formData.append('file', file);
      formData.append('algorithm', 'chacha20');

      fetch('/encrypt', {
          method: 'POST',
          body: formData
      })
      .then(response => {
          if (!response.ok) {
              throw new Error('Encryption failed');
          }
          const key = response.headers.get('Key');
          const nonce = response.headers.get('nonce');
          encryptionDetails.textContent = `Key: ${key}\nNonce: ${nonce}`;
          return response.blob();
      })
      .then(blob => {
          const url = URL.createObjectURL(blob);
          downloadLink.href = url;
          downloadLink.download = `${file.name}.enc`;
          downloadLink.style.display = 'inline-block';
          downloadLink.textContent = 'Download Encrypted File';
      })
      .catch(error => {
          console.error('Error:', error);
          alert('Encryption failed. Please try again.');
      });
  });

  decryptButton.addEventListener('click', () => {
      const file = decryptFileInput.files[0];
      const key = decryptKey.value;
      const nonce = decryptNonce.value;

      if (!file || !key || !nonce) {
          alert('Please provide a file, key, and nonce for decryption');
          return;
      }

      const formData = new FormData();
      formData.append('file', file);
      formData.append('key', key);
      formData.append('nonce', nonce);
      formData.append('algorithm', 'chacha20');

      fetch('/decrypt', {
          method: 'POST',
          body: formData
      })
      .then(response => {
          if (!response.ok) {
              throw new Error('Decryption failed');
          }
          return response.blob();
      })
      .then(blob => {
          const url = URL.createObjectURL(blob);
          decryptDownloadLink.href = url;
          decryptDownloadLink.download = file.name.replace('.enc', '.dec');
          decryptDownloadLink.style.display = 'inline-block';
          decryptDownloadLink.textContent = 'Download Decrypted File';
          decryptionDetails.textContent = 'Decryption successful!';
      })
      .catch(error => {
          console.error('Error:', error);
          alert('Decryption failed. Please check your key and nonce.');
      });
  });
});