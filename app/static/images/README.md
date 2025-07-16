# Website Images

This directory contains all images used by the e-commerce website.

## Directory Structure

```
app/static/images/
├── products/          # Product images
│   ├── iphone15pro.jpg
│   ├── samsung-s24.jpg
│   ├── macbook-air-m3.jpg
│   ├── nike-airmax-270.jpg
│   └── python-book.jpg
├── categories/        # Category icons
│   ├── electronics.png
│   ├── clothing.png
│   ├── books.png
│   └── home.png
├── icons/            # Additional icons (if needed)
├── logo.png          # Website logo
├── favicon.ico       # Browser favicon
└── placeholder.jpg   # Default placeholder image
```

## Image Specifications

### Product Images
- **Size**: 300x200 pixels
- **Format**: JPG
- **Purpose**: Display on product cards and detail pages

### Category Icons
- **Size**: 64x64 pixels
- **Format**: PNG
- **Purpose**: Category filtering and navigation

### Website Assets
- **Logo**: 200x60 pixels
- **Favicon**: 32x32 pixels
- **Placeholder**: 300x200 pixels

## Usage

### In HTML Templates
```html
<img src="/static/images/products/iphone15pro.jpg" alt="iPhone 15 Pro">
<img src="/static/images/categories/electronics.png" alt="Electronics">
```

### In JavaScript
```javascript
const imageUrl = '/static/images/products/' + product.image_filename;
```

### Fallback Image
```html
<img src="${product.image_url || '/static/images/placeholder.jpg'}" alt="Product">
```

## Adding New Images

1. Place new product images in `products/` directory
2. Place new category icons in `categories/` directory
3. Update the database with the new image URLs
4. Use relative paths starting with `/static/images/`

## Image Optimization

For production use, consider:
- Compressing images for faster loading
- Using WebP format for better compression
- Implementing lazy loading for product images
- Creating multiple sizes for responsive design 