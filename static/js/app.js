// Locography JavaScript

const API_BASE = '/api/v1';

// State
let currentTab = 'items';
let items = [];
let locations = [];
let categories = [];

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    initTabs();
    initModals();
    initButtons();
    loadData();
});

// Tab Management
function initTabs() {
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const tabName = tab.dataset.tab;
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    // Update active tab button
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.tab === tabName);
    });

    // Update active content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.toggle('active', content.id === `${tabName}-tab`);
    });

    currentTab = tabName;
}

// Modal Management
function initModals() {
    // Item modal
    const itemModal = document.getElementById('item-modal');
    const itemClose = itemModal.querySelector('.close');
    const cancelItem = document.getElementById('cancel-item');

    itemClose.onclick = () => itemModal.classList.remove('show');
    cancelItem.onclick = () => itemModal.classList.remove('show');

    // Location modal
    const locationModal = document.getElementById('location-modal');
    const locationClose = locationModal.querySelector('.close');
    const cancelLocation = document.getElementById('cancel-location');

    locationClose.onclick = () => locationModal.classList.remove('show');
    cancelLocation.onclick = () => locationModal.classList.remove('show');

    // Category modal
    const categoryModal = document.getElementById('category-modal');
    const categoryClose = categoryModal.querySelector('.close');
    const cancelCategory = document.getElementById('cancel-category');

    categoryClose.onclick = () => categoryModal.classList.remove('show');
    cancelCategory.onclick = () => categoryModal.classList.remove('show');

    // Close on outside click
    window.onclick = (event) => {
        if (event.target.classList.contains('modal')) {
            event.target.classList.remove('show');
        }
    };
}

// Button Handlers
function initButtons() {
    document.getElementById('add-item-btn').addEventListener('click', showAddItemModal);
    document.getElementById('add-location-btn').addEventListener('click', showAddLocationModal);
    document.getElementById('add-category-btn').addEventListener('click', showAddCategoryModal);
    
    document.getElementById('item-form').addEventListener('submit', handleItemSubmit);
    document.getElementById('location-form').addEventListener('submit', handleLocationSubmit);
    document.getElementById('category-form').addEventListener('submit', handleCategorySubmit);
    
    document.getElementById('text-search-btn').addEventListener('click', handleTextSearch);
    document.getElementById('image-search-btn').addEventListener('click', handleImageSearch);
    
    document.getElementById('items-search').addEventListener('input', filterItems);
}

// Load Data
async function loadData() {
    await Promise.all([
        loadItems(),
        loadLocations(),
        loadCategories()
    ]);
}

async function loadItems() {
    try {
        const response = await fetch(`${API_BASE}/items`);
        items = await response.json();
        renderItems(items);
    } catch (error) {
        console.error('Error loading items:', error);
    }
}

async function loadLocations() {
    try {
        const response = await fetch(`${API_BASE}/locations`);
        locations = await response.json();
        renderLocations(locations);
        updateLocationSelect();
    } catch (error) {
        console.error('Error loading locations:', error);
    }
}

async function loadCategories() {
    try {
        const response = await fetch(`${API_BASE}/categories`);
        categories = await response.json();
        renderCategories(categories);
        updateCategorySelect();
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

// Render Functions
function renderItems(itemsList) {
    const container = document.getElementById('items-list');
    
    if (itemsList.length === 0) {
        container.innerHTML = '<div class="empty-state"><h3>No items yet</h3><p>Add your first item to get started</p></div>';
        return;
    }

    container.innerHTML = itemsList.map(item => `
        <div class="item-card" onclick="viewItem(${item.id})">
            <h3>${item.name}</h3>
            <p>${item.description || 'No description'}</p>
            ${item.location_id ? `<p>📍 Location: ${getLocationName(item.location_id)}</p>` : ''}
            ${item.quantity ? `<p>📦 Quantity: ${item.quantity} ${item.unit || ''}</p>` : ''}
            ${item.tags && item.tags.length ? `
                <div class="item-tags">
                    ${item.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                </div>
            ` : ''}
        </div>
    `).join('');
}

function renderLocations(locationsList) {
    const container = document.getElementById('locations-list');
    
    if (locationsList.length === 0) {
        container.innerHTML = '<div class="empty-state"><h3>No locations yet</h3><p>Add storage locations to organize your items</p></div>';
        return;
    }

    container.innerHTML = locationsList.map(location => `
        <div class="location-card">
            <h3>${location.name}</h3>
            <p>${location.description || 'No description'}</p>
            ${location.location_type ? `<p>Type: ${location.location_type}</p>` : ''}
        </div>
    `).join('');
}

function renderCategories(categoriesList) {
    const container = document.getElementById('categories-list');
    
    if (categoriesList.length === 0) {
        container.innerHTML = '<div class="empty-state"><h3>No categories yet</h3><p>Add categories to organize your inventory</p></div>';
        return;
    }

    container.innerHTML = categoriesList.map(category => `
        <div class="category-item">
            <h3>${category.name}</h3>
            <p>${category.description || 'No description'}</p>
        </div>
    `).join('');
}

// Modal Show Functions
function showAddItemModal() {
    document.getElementById('item-form').reset();
    document.getElementById('item-modal').classList.add('show');
}

function showAddLocationModal() {
    document.getElementById('location-form').reset();
    document.getElementById('location-modal').classList.add('show');
}

function showAddCategoryModal() {
    document.getElementById('category-form').reset();
    document.getElementById('category-modal').classList.add('show');
}

// Form Submit Handlers
async function handleItemSubmit(e) {
    e.preventDefault();
    
    const formData = {
        name: document.getElementById('item-name').value,
        description: document.getElementById('item-description').value,
        category_id: parseInt(document.getElementById('item-category').value) || null,
        location_id: parseInt(document.getElementById('item-location').value) || null,
        quantity: parseInt(document.getElementById('item-quantity').value) || 1,
        unit: document.getElementById('item-unit').value,
        estimated_value: parseFloat(document.getElementById('item-value').value) || null,
        tags: document.getElementById('item-tags').value.split(',').map(t => t.trim()).filter(t => t)
    };

    try {
        const response = await fetch(`${API_BASE}/items`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            const newItem = await response.json();
            
            // Handle image upload if present
            const imageFile = document.getElementById('item-image').files[0];
            if (imageFile) {
                const imageFormData = new FormData();
                imageFormData.append('file', imageFile);
                imageFormData.append('is_primary', 'true');
                
                await fetch(`${API_BASE}/items/${newItem.id}/images`, {
                    method: 'POST',
                    body: imageFormData
                });
            }
            
            document.getElementById('item-modal').classList.remove('show');
            await loadItems();
        }
    } catch (error) {
        console.error('Error creating item:', error);
        alert('Error creating item');
    }
}

async function handleLocationSubmit(e) {
    e.preventDefault();
    
    const formData = {
        name: document.getElementById('location-name').value,
        description: document.getElementById('location-description').value,
        location_type: document.getElementById('location-type').value || null
    };

    try {
        const response = await fetch(`${API_BASE}/locations`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            document.getElementById('location-modal').classList.remove('show');
            await loadLocations();
        }
    } catch (error) {
        console.error('Error creating location:', error);
        alert('Error creating location');
    }
}

async function handleCategorySubmit(e) {
    e.preventDefault();
    
    const formData = {
        name: document.getElementById('category-name').value,
        description: document.getElementById('category-description').value
    };

    try {
        const response = await fetch(`${API_BASE}/categories`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            document.getElementById('category-modal').classList.remove('show');
            await loadCategories();
        }
    } catch (error) {
        console.error('Error creating category:', error);
        alert('Error creating category');
    }
}

// Search Functions
async function handleTextSearch() {
    const query = document.getElementById('text-search').value;
    
    try {
        const response = await fetch(`${API_BASE}/search/items?q=${encodeURIComponent(query)}`);
        const results = await response.json();
        
        const container = document.getElementById('search-results');
        if (results.length === 0) {
            container.innerHTML = '<div class="empty-state"><h3>No results found</h3></div>';
        } else {
            renderSearchResults(results);
        }
    } catch (error) {
        console.error('Error searching:', error);
    }
}

async function handleImageSearch() {
    const fileInput = document.getElementById('image-search-input');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Please select an image');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_BASE}/search/by-image?limit=10&threshold=0.3`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        
        const container = document.getElementById('search-results');
        if (data.results.length === 0) {
            container.innerHTML = '<div class="empty-state"><h3>No similar items found</h3></div>';
        } else {
            renderSearchResults(data.results.map(r => ({...r.item, similarity: r.similarity})));
        }
    } catch (error) {
        console.error('Error searching by image:', error);
        alert('Error searching by image');
    }
}

function renderSearchResults(results) {
    const container = document.getElementById('search-results');
    
    container.innerHTML = results.map(item => `
        <div class="item-card">
            <h3>${item.name}</h3>
            <p>${item.description || 'No description'}</p>
            ${item.similarity ? `<p>Similarity: ${(item.similarity * 100).toFixed(1)}%</p>` : ''}
            ${item.location_id ? `<p>📍 ${getLocationName(item.location_id)}</p>` : ''}
            ${item.tags && item.tags.length ? `
                <div class="item-tags">
                    ${item.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                </div>
            ` : ''}
        </div>
    `).join('');
}

function filterItems() {
    const query = document.getElementById('items-search').value.toLowerCase();
    const filtered = items.filter(item => 
        item.name.toLowerCase().includes(query) || 
        (item.description && item.description.toLowerCase().includes(query))
    );
    renderItems(filtered);
}

// Helper Functions
function getLocationName(locationId) {
    const location = locations.find(l => l.id === locationId);
    return location ? location.name : 'Unknown';
}

function getCategoryName(categoryId) {
    const category = categories.find(c => c.id === categoryId);
    return category ? category.name : 'Unknown';
}

function updateLocationSelect() {
    const select = document.getElementById('item-location');
    select.innerHTML = '<option value="">Select location</option>' +
        locations.map(l => `<option value="${l.id}">${l.name}</option>`).join('');
}

function updateCategorySelect() {
    const select = document.getElementById('item-category');
    select.innerHTML = '<option value="">Select category</option>' +
        categories.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
}

function viewItem(itemId) {
    // Future enhancement: show detailed item view
    console.log('View item:', itemId);
}
