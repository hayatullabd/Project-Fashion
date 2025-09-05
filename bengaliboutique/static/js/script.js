function addToCart(productId, variantId = null) {
    const body = variantId ? { variant_id: variantId } : {};
    fetch(`/cart/add/${productId}/`, { 
        method: 'POST',
        headers: { 
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(body)
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alert('Added to cart!');
            } else {
                alert(data.error || 'Error adding to cart');
            }
        });
}

function removeFromCart(productId, variantId = null) {
    const body = variantId ? { variant_id: variantId } : {};
    fetch(`/cart/remove/${productId}/`, { 
        method: 'POST',
        headers: { 
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(body)
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                location.reload();
            }
        });
}

function updateCart(productId, quantity, variantId = null) {
    const body = { product_id: productId, quantity: quantity };
    if (variantId) body.variant_id = variantId;
    fetch('/api/cart/update/', {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value 
        },
        body: JSON.stringify(body)
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert(data.error || 'Error updating cart');
            }
        });
}

function addToWishlist(productId) {
    fetch(`/wishlist/add/${productId}/`, { 
        method: 'POST',
        headers: { 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value }
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alert('Added to wishlist!');
            }
        });
}

function removeFromWishlist(productId) {
    fetch(`/wishlist/remove/${productId}/`, { 
        method: 'POST',
        headers: { 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value }
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                location.reload();
            }
        });
}

function filterProducts(category) {
    fetch(`/api/products/filter/?category=${category}`)
        .then(res => res.json())
        .then(data => {
            const grid = document.getElementById('product-grid');
            grid.innerHTML = '';
            data.products.forEach(p => {
                grid.innerHTML += `
                    <div class="bg-white dark:bg-gray-800 rounded-lg shadow" data-aos="zoom-in">
                        ${p.discount ? `<span class="absolute top-2 left-2 bg-red-500 text-white px-2 py-1 rounded">${p.discount}% OFF</span>` : ''}
                        <img src="${p.image}" alt="${p.name}" class="w-full h-48 object-cover rounded-t-lg lazy" loading="lazy">
                        <div class="p-4">
                            <h3 class="text-xl font-semibold">${p.name}</h3>
                            <p>${p.description || 'Explore our collection'}</p>
                            <div class="flex items-center gap-2 mt-2">
                                <span class="text-lg font-bold">৳${p.price}</span>
                                ${p.discount ? `<span class="line-through text-gray-500">৳${p.original_price}</span>` : ''}
                            </div>
                            <button onclick="addToCart(${p.id})" class="bg-green-500 text-white px-4 py-2 mt-2 rounded hover:bg-green-600">Add to Cart</button>
                        </div>
                    </div>`;
            });
            AOS.refresh();
        });
}

document.getElementById('filter-form')?.addEventListener('submit', e => {
    e.preventDefault();
    const params = new URLSearchParams(new FormData(e.target));
    fetch(`/api/products/filter/?${params.toString()}`)
        .then(res => res.json())
        .then(data => {
            const grid = document.getElementById('product-grid');
            grid.innerHTML = '';
            data.products.forEach(p => {
                grid.innerHTML += `
                    <div class="bg-white dark:bg-gray-800 rounded-lg shadow" data-aos="zoom-in">
                        ${p.discount ? `<span class="absolute top-2 left-2 bg-red-500 text-white px-2 py-1 rounded">${p.discount}% OFF</span>` : ''}
                        <img src="${p.image}" alt="${p.name}" class="w-full h-48 object-cover rounded-t-lg lazy" loading="lazy">
                        <div class="p-4">
                            <h3 class="text-xl font-semibold">${p.name}</h3>
                            <p>${p.description || 'Explore our collection'}</p>
                            <div class="flex items-center gap-2 mt-2">
                                <span class="text-lg font-bold">৳${p.price}</span>
                                ${p.discount ? `<span class="line-through text-gray-500">৳${p.original_price}</span>` : ''}
                            </div>
                            <button onclick="addToCart(${p.id})" class="bg-green-500 text-white px-4 py-2 mt-2 rounded hover:bg-green-600">Add to Cart</button>
                        </div>
                    </div>`;
            });
            AOS.refresh();
        });
});

const searchInput = document.querySelector('#search-input');
const suggestionsDiv = document.querySelector('#search-suggestions');
if (searchInput) {
    searchInput.addEventListener('input', e => {
        if (e.target.value.length > 2) {
            fetch(`/api/products/filter/?q=${e.target.value}`)
                .then(res => res.json())
                .then(data => {
                    suggestionsDiv.innerHTML = '';
                    suggestionsDiv.classList.remove('hidden');
                    data.products.slice(0, 5).forEach(p => {
                        suggestionsDiv.innerHTML += `<a href="/products/${p.slug}/" class="block p-2 hover:bg-gray-200 dark:hover:bg-gray-700">${p.name}</a>`;
                    });
                    if (!data.products.length) suggestionsDiv.classList.add('hidden');
                });
        } else {
            suggestionsDiv.classList.add('hidden');
        }
    });
    document.addEventListener('click', e => {
        if (!searchInput.contains(e.target) && !suggestionsDiv.contains(e.target)) {
            suggestionsDiv.classList.add('hidden');
        }
    });
}

document.getElementById('theme-toggle').addEventListener('click', () => {
    document.body.classList.toggle('dark');
    localStorage.theme = document.body.classList.contains('dark') ? 'dark' : 'light';
    document.getElementById('theme-toggle').textContent = document.body.classList.contains('dark') ? '☀️' : '🌙';
});
if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    document.body.classList.add('dark');
    document.getElementById('theme-toggle').textContent = '☀️';
} else {
    document.getElementById('theme-toggle').textContent = '🌙';
}

// Toggle bKash instructions
document.querySelectorAll('input[name="payment"]').forEach(input => {
    input.addEventListener('change', () => {
        const bkashInstructions = document.getElementById('bkash-instructions');
        if (input.value === 'bkash') {
            bkashInstructions.classList.remove('hidden');
        } else {
            bkashInstructions.classList.add('hidden');
        }
    });
});