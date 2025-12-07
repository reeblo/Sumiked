//integracion del navbar y footer
fetch("navbar.html")
  .then((r) => r.text())
  .then((t) => (document.getElementById("navbar-include").innerHTML = t));
fetch("footer.html")
  .then((r) => r.text())
  .then((t) => (document.getElementById("footer-include").innerHTML = t));

//funciones en el navbar
// Script para manejar el submenú del dropdown
document.querySelectorAll(".dropdown-submenu > a").forEach(function (element) {
  element.addEventListener("click", function (e) {
    e.preventDefault();
    e.stopPropagation();
    let submenu = this.nextElementSibling;
    if (submenu) {
      submenu.style.display =
        submenu.style.display === "block" ? "none" : "block";
    }
  });
});

// Cerrar menú al hacer click en un enlace en móviles
document.querySelectorAll(".navbar-nav .nav-link").forEach((link) => {
  link.addEventListener("click", () => {
    const navbarCollapse = document.querySelector(".navbar-collapse");
    if (navbarCollapse.classList.contains("show")) {
      const bsCollapse = new bootstrap.Collapse(navbarCollapse);
      bsCollapse.hide();
    }
  });
});

// Asegurar que los dropdowns funcionen en móvil
document.querySelectorAll(".dropdown-toggle").forEach((toggle) => {
  toggle.addEventListener("click", function (e) {
    if (window.innerWidth < 992) {
      e.preventDefault();
      const dropdown = this.nextElementSibling;
      dropdown.style.display =
        dropdown.style.display === "block" ? "none" : "block";
    }
  });
});

// funciones inicio
// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", function (e) {
    e.preventDefault();
    document.querySelector(this.getAttribute("href")).scrollIntoView({
      behavior: "smooth",
    });
  });
});

// Efecto parallax para el hero section
window.addEventListener("scroll", function () {
  const hero = document.querySelector(".hero-section");
  if (hero) {
    const scrollPosition = window.pageYOffset;
    hero.style.backgroundPositionY = scrollPosition * 0.5 + "px";
  }
});

//nuevos

// Funciones para el panel de administración
document.addEventListener("DOMContentLoaded", function () {
  const productModal = new bootstrap.Modal(
    document.getElementById("productModal")
  );
  const productForm = document.getElementById("productForm");
  const saveButton = document.getElementById("saveProduct");

  // Previsualización de imagen
  document
    .getElementById("productImage")
    .addEventListener("input", function () {
      const preview = document.getElementById("imagePreview");
      if (this.value) {
        preview.innerHTML = `<img src="${this.value}" class="product-image-preview mt-2" style="max-width: 200px;">`;
      } else {
        preview.innerHTML = "";
      }
    });

  // Agregar producto
  saveButton.addEventListener("click", async function () {
    const formData = new FormData(productForm);
    const productData = Object.fromEntries(formData);

    // Convertir a tipos correctos
    productData.price = parseFloat(productData.price);
    productData.stock = parseInt(productData.stock);

    try {
      const response = await fetch("/api/products", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(productData),
      });

      const result = await response.json();

      if (result.success) {
        location.reload(); // Recargar para mostrar el nuevo producto
      } else {
        alert("Error al guardar el producto");
      }
    } catch (error) {
      console.error("Error:", error);
      alert("Error de conexión");
    }
  });

  // Editar producto
  document.querySelectorAll(".edit-product").forEach((button) => {
    button.addEventListener("click", function () {
      const product = JSON.parse(this.dataset.product);

      // Llenar el formulario
      document.getElementById("productId").value = product.id;
      document.getElementById("productName").value = product.name;
      document.getElementById("productDescription").value =
        product.description || "";
      document.getElementById("productPrice").value = product.price;
      document.getElementById("productCategory").value = product.category;
      document.getElementById("productStock").value = product.stock;
      document.getElementById("productImage").value = product.image_url || "";

      // Actualizar título del modal
      document.getElementById("modalTitle").textContent = "Editar Producto";

      // Mostrar previsualización
      if (product.image_url) {
        document.getElementById(
          "imagePreview"
        ).innerHTML = `<img src="${product.image_url}" class="product-image-preview mt-2" style="max-width: 200px;">`;
      }

      productModal.show();
    });
  });

  // Eliminar producto
  document.querySelectorAll(".delete-product").forEach((button) => {
    button.addEventListener("click", async function () {
      const productId = this.dataset.productId;

      if (confirm("¿Estás seguro de que quieres eliminar este producto?")) {
        try {
          const response = await fetch(`/api/products/${productId}`, {
            method: "DELETE",
          });

          const result = await response.json();

          if (result.success) {
            document
              .querySelector(`tr[data-product-id="${productId}"]`)
              .remove();
          } else {
            alert("Error al eliminar el producto");
          }
        } catch (error) {
          console.error("Error:", error);
          alert("Error de conexión");
        }
      }
    });
  });

  // Limpiar formulario al cerrar modal
  document
    .getElementById("productModal")
    .addEventListener("hidden.bs.modal", function () {
      productForm.reset();
      document.getElementById("productId").value = "";
      document.getElementById("imagePreview").innerHTML = "";
      document.getElementById("modalTitle").textContent = "Agregar Producto";
    });
});
//mejoraS
// Inicializar tooltips de Bootstrap
document.addEventListener("DOMContentLoaded", function () {
  var tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]')
  );
  var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
});
//mensaje de gracias a ti

function mostrarMensajeDesarrollo() {
  // Puedes usar un alert simple o algo más elegante
  alert("⚙️ Esta sección está en desarrollo y estará disponible próximamente.");
  return false;
}
