const modal = document.querySelector('#login-modal');

const carGallery = document.querySelector('[data-car-gallery]');
if (carGallery) {
  const vehicles = [
    {
      title: 'MARUTI SUZUKI VITARA BREEZA VDI AMT',
      description: 'Single ownership, diesel, automatic transmission, and full showroom service record.',
      details: {
        price: '\u20B9645,000.00',
        'make-model': 'Vitara Breeza VDI AMT',
        year: '2018 / 2018',
        ownership: 'Single owner',
        km: '120K km',
        fuel: 'Diesel',
        transmission: 'Automatic (AMT)',
        registration: 'TN 18',
        number: 'Not provided',
        service: 'Full showroom record',
        insurance: 'Expired',
        tyres: 'Not provided',
      },
      image: '/static/images/WhatsApp%20Product%202026-09-30%20at%2012.59.00%20PM.jpeg',
      alt: 'Maruti Suzuki Vitara Breeza VDI AMT from The Maaran Cars',
    },
    {
      title: 'AUDI A4 35TDI PREMIUM PLUS WITH SUNROOF',
      description: 'Single ownership, proper showroom service record, and tyres with 50-60% life remaining.',
      details: {
        price: '\u20B9920,000.00',
        'make-model': 'A4 35TDI Premium Plus (Top End) with Sunroof',
        year: '2012 / 2012',
        ownership: 'Single owner',
        km: '96K km',
        fuel: 'Diesel',
        transmission: 'Automatic',
        registration: 'TN registered',
        number: '0050',
        service: 'Proper showroom record',
        insurance: 'Expired',
        tyres: '50-60% remaining',
      },
      image: '/static/images/WhatsApp%20Product%202026-09-30%20at%204.18.32%20PM.jpeg',
      alt: 'Audi A4 35TDI Premium Plus with sunroof',
    },
    {
      title: 'TATA HEXA 4*2 XTA AUTOMATIC (7 SEATER)',
      description: 'Single ownership, diesel automatic, seven seats, and full showroom service record.',
      details: {
        price: '\u20B91,075,000.00',
        'make-model': 'Hexa 4*2 XTA Auto (7 seater)',
        year: '2017 / 2018',
        ownership: 'Single owner',
        km: '130K km',
        fuel: 'Diesel',
        transmission: 'Automatic',
        registration: 'Tirupur registered',
        number: 'Fancy number',
        service: 'Full showroom record',
        insurance: 'Live',
        tyres: 'Not provided',
      },
      image: '/static/images/WhatsApp%20Product%202026-09-30%20at%204.21.34%20PM.jpeg',
      alt: 'Tata Hexa 4 by 2 XTA automatic seven seater',
    },
  ];
  let activeVehicle = 0;
  const galleryImage = carGallery.querySelector('[data-gallery-image]');
  const galleryCount = carGallery.querySelector('[data-gallery-count]');

  const showVehicle = (index) => {
    activeVehicle = (index + vehicles.length) % vehicles.length;
    const vehicle = vehicles[activeVehicle];
    galleryImage.src = vehicle.image;
    galleryImage.alt = vehicle.alt;
    carGallery.querySelector('[data-gallery-title]').textContent = vehicle.title;
    carGallery.querySelector('[data-gallery-description]').textContent = vehicle.description;
    Object.entries(vehicle.details).forEach(([key, value]) => {
      carGallery.querySelector(`[data-gallery-spec-value="${key}"]`).textContent = value;
    });
    galleryCount.textContent = `${String(activeVehicle + 1).padStart(2, '0')} / ${String(vehicles.length).padStart(2, '0')}`;
  };

  carGallery.querySelectorAll('[data-gallery-next]').forEach((button) => {
    button.addEventListener('click', () => showVehicle(activeVehicle + 1));
  });
  carGallery.querySelector('[data-gallery-previous]').addEventListener('click', () => {
    showVehicle(activeVehicle - 1);
  });
  showVehicle(0);
}

function setMessage(form, message, type = '') {
  const target = form.querySelector('.form-message');
  target.textContent = message;
  target.className = `form-message ${type}`;
}

function setModal(open) {
  modal.classList.toggle('is-open', open);
  modal.setAttribute('aria-hidden', String(!open));
  if (open) modal.querySelector('input').focus();
}

document.querySelectorAll('[data-modal-open]').forEach((button) => {
  button.addEventListener('click', () => setModal(true));
});
document.querySelectorAll('[data-modal-close]').forEach((button) => {
  button.addEventListener('click', () => setModal(false));
});
document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') setModal(false);
});

document.querySelectorAll('.account-form').forEach((form) => {
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const submit = form.querySelector('.form-submit');
    submit.disabled = true;
    setMessage(form, 'Creating your account...');
    try {
      const response = await fetch(`/api/register/${form.dataset.role}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(Object.fromEntries(new FormData(form))),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.message);
      setMessage(form, result.message, 'success');
      form.reset();
    } catch (error) {
      setMessage(form, error.message || 'Something went wrong.', 'error');
    } finally {
      submit.disabled = false;
    }
  });
});

document.querySelector('#login-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const submit = form.querySelector('.form-submit');
  submit.disabled = true;
  setMessage(form, 'Signing you in...');
  try {
    const response = await fetch('/api/admin/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(Object.fromEntries(new FormData(form))),
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.message);
    window.location.href = '/admin/dashboard';
  } catch (error) {
    setMessage(form, error.message || 'Something went wrong.', 'error');
  } finally {
    submit.disabled = false;
  }
});

const reportTable = document.querySelector('.report-table');
if (reportTable) {
  const sortableHeaders = reportTable.querySelectorAll('th[data-sort]');
  const rows = Array.from(reportTable.querySelectorAll('tbody tr'));

  const sortRows = (index, direction) => {
    const sorted = [...rows].sort((a, b) => {
      const left = a.children[index].textContent.trim();
      const right = b.children[index].textContent.trim();
      const leftNumber = Number(left.replace(/[^0-9.-]/g, ''));
      const rightNumber = Number(right.replace(/[^0-9.-]/g, ''));
      if (!Number.isNaN(leftNumber) && !Number.isNaN(rightNumber)) {
        return direction * (leftNumber - rightNumber);
      }
      return direction * left.localeCompare(right);
    });

    const tbody = reportTable.querySelector('tbody');
    tbody.innerHTML = '';
    sorted.forEach((row) => tbody.appendChild(row));
  };

  sortableHeaders.forEach((header) => {
    header.addEventListener('click', () => {
      const direction = header.dataset.direction === 'asc' ? -1 : 1;
      header.dataset.direction = direction === 1 ? 'asc' : 'desc';
      sortRows(Number(header.dataset.index), direction);
    });
  });
}
