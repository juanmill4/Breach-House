window.toggleMobileNav = function () {
    const nav = document.getElementById('mobileNav');
    const hamburger = document.getElementById('hamburger');
    const closeIcon = document.getElementById('closeIcon');

    nav.classList.toggle('show');

    const isVisible = nav.classList.contains('show');
    hamburger.style.display = isVisible ? 'none' : 'block';
    closeIcon.style.display = isVisible ? 'block' : 'none';
  };

  document.querySelectorAll('.nav-link.dropdown-toggle').forEach(link => {
    link.addEventListener('click', function (e) {
      e.preventDefault();
  
      
      this.classList.toggle('active');
  
      
      let submenu = this.nextElementSibling;
      
    
      const icon = this.querySelector('.dropdown-icon');
  
      
      if (this.classList.contains('active')) {
        
        icon.innerHTML = `
          <svg class="dropdown-icon" width="24px" height="24px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" stroke="#ffffff">
            <g id="SVGRepo_iconCarrier">
              <path d="M9 12H15" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path>
            </g>
          </svg>
        `;
      } else {
        
        icon.innerHTML = `
          <svg class="dropdown-icon" width="24px" height="24px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" stroke="#ffffff">
            <g id="SVGRepo_iconCarrier">
              <path d="M9 12H15" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path>
              <path d="M12 9L12 15" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path>
            </g>
          </svg>
        `;
      }
  
      if (submenu && submenu.classList.contains('submenu')) {
        if (submenu.style.maxHeight) {
          submenu.style.maxHeight = null; 
        } else {
          submenu.style.maxHeight = `${submenu.scrollHeight}px`; 
        }
      }
    });
  });
  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});
