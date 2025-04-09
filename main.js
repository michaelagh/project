
document.querySelector('.render-btn').addEventListener('click', async () => {

    const vesCode = document.querySelector('.text-area').value;
  
    const activeFilterBtn = document.querySelector('.filter-button.active');
    const filter = activeFilterBtn ? activeFilterBtn.textContent.trim() : 'ORIGINAL';
  
    try {
      const response = await fetch('/render', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          code: vesCode,
          filter: filter
        })
      });
  
      if (!response.ok) {
        throw new Error('Nepodarilo sa načítať obrázok');
      }
  
      const blob = await response.blob();
      const imgURL = URL.createObjectURL(blob);
      document.querySelector('.center-image').src = imgURL;
    } catch (error) {
      console.error('Chyba pri renderovaní:', error);
    }
  });
  
  document.querySelectorAll('.filter-button').forEach(button => {
    button.addEventListener('click', () => {
      document.querySelectorAll('.filter-button').forEach(btn => btn.classList.remove('active'));
      button.classList.add('active');
    });
  });
  