// PocketSmart AI Client Interaction Engine

function formatINR(val) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }).format(val);
}

function showToast(message, type = 'info') {
  let toast = document.getElementById('ps-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'ps-toast';
    toast.style.position = 'fixed';
    toast.style.bottom = '24px';
    toast.style.right = '24px';
    toast.style.zIndex = '9999';
    toast.style.padding = '12px 20px';
    toast.style.borderRadius = '9999px';
    toast.style.fontSize = '0.9rem';
    toast.style.fontWeight = '600';
    toast.style.boxShadow = '0 10px 30px rgba(0,0,0,0.5)';
    toast.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
    toast.style.backdropFilter = 'blur(16px)';
    document.body.appendChild(toast);
  }

  if (type === 'error') {
    toast.style.background = 'rgba(244, 63, 94, 0.9)';
    toast.style.color = '#fff';
  } else if (type === 'success') {
    toast.style.background = 'rgba(16, 185, 129, 0.9)';
    toast.style.color = '#fff';
  } else {
    toast.style.background = 'rgba(99, 102, 241, 0.9)';
    toast.style.color = '#fff';
  }

  toast.textContent = message;
  toast.style.opacity = '1';
  toast.style.transform = 'translateY(0)';

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
  }, 3500);
}

// User logout handler
async function handleLogout() {
  try {
    const res = await fetch('/logout', { method: 'POST' });
    if (res.ok) {
      window.location.href = '/';
    }
  } catch (err) {
    console.error('Logout error:', err);
  }
}

// Check session on load
document.addEventListener('DOMContentLoaded', () => {
  // Sync range sliders with labels
  document.querySelectorAll('.range-slider').forEach(slider => {
    const displayId = slider.dataset.display;
    const displayEl = document.getElementById(displayId);
    if (displayEl) {
      const update = () => {
        const val = parseFloat(slider.value);
        if (slider.dataset.currency === 'true') {
          displayEl.textContent = formatINR(val);
        } else {
          displayEl.textContent = val;
        }
      };
      slider.addEventListener('input', update);
      update();
    }
  });

  // Setup file preview dropzones
  const dropzone = document.getElementById('outfit-dropzone');
  const fileInput = document.getElementById('outfit-image-input');
  const previewImg = document.getElementById('dropzone-preview');

  if (dropzone && fileInput) {
    dropzone.addEventListener('click', () => fileInput.click());
    dropzone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropzone.classList.add('dragover');
    });
    dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));
    dropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropzone.classList.remove('dragover');
      if (e.dataTransfer.files.length > 0) {
        fileInput.files = e.dataTransfer.files;
        showFilePreview(fileInput.files[0]);
      }
    });
    fileInput.addEventListener('change', () => {
      if (fileInput.files.length > 0) {
        showFilePreview(fileInput.files[0]);
      }
    });

    function showFilePreview(file) {
      if (file && previewImg) {
        const reader = new FileReader();
        reader.onload = (e) => {
          previewImg.src = e.target.result;
          previewImg.style.display = 'block';
        };
        reader.readAsDataURL(file);
      }
    }
  }
});
