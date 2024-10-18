import React, { useEffect, useState } from 'react';
import Pagination from './Pagination';
import placeholderImage from '../assets/placeholder-image.png'; // Add a placeholder image

const ProductTable = ({ products = [] }) => {
    const [currentPage, setCurrentPage] = useState(1);
    const itemsPerPage = 5; // Set your items per page
    const totalItems = products.length;
    const totalPages = Math.ceil(totalItems / itemsPerPage);

    // State to store the current image index for each product
    const [currentImageIndex, setCurrentImageIndex] = useState({});

    // Slice products for the current page
    const currentProducts = products.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

    // Initialize image index for each product
    useEffect(() => {
        const initialImageIndexes = {};
        products.forEach((product, index) => {
            initialImageIndexes[index] = 0; // Set first image as default for each product
        });
        setCurrentImageIndex(initialImageIndexes);
    }, [products]);

    // Handle next image click
    const handleNextImage = (productIndex, totalImages) => {
        setCurrentImageIndex((prevIndexes) => ({
            ...prevIndexes,
            [productIndex]: (prevIndexes[productIndex] + 1) % totalImages,
        }));
    };

    // Handle previous image click
    const handlePreviousImage = (productIndex, totalImages) => {
        setCurrentImageIndex((prevIndexes) => ({
            ...prevIndexes,
            [productIndex]: (prevIndexes[productIndex] - 1 + totalImages) % totalImages,
        }));
    };

    useEffect(() => {
        console.log('Updated Products in ProductTable: ', products);
    }, [products]);

    // Function to export CSV
    const exportToCSV = () => {
        const csvData = products.map(product => ({
            Name: product.product_name,
            Price: product.product_price || 'Price not available',
            Link: product.link
        }));

        const csvRows = [
            ['Name', 'Price', 'Link'], // Header row
            ...csvData.map(row => [row.Name.replace(',', ''), row.Price.replace(',', '.'), row.Link])
        ];

        const csvContent = "data:text/csv;charset=utf-8,"
            + csvRows.map(e => e.join(",")).join("\n");

        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", "products.csv");
        document.body.appendChild(link); // Required for Firefox
        link.click();
    };

    return (
        <div className="max-w-[1280px] mx-auto pb-28 ">
            <div className="w-full flex justify-between items-center mb-3 mt-12 pl-3">
                <div>
                    <h3 className="text-lg font-semibold text-slate-800">Furniture Products extracted</h3>
                    <p className="text-slate-500">This is what I found!</p>
                </div>

                {/* Export to CSV Button */}
                <button
                    className="flex items-center space-x-2 bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded"
                    onClick={() => exportToCSV(products)}
                >
                    {/* SVG Icon for Download */}
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        strokeWidth="2"
                        stroke="currentColor"
                        className="w-6 h-6"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2m-4-4l-4 4m0 0l-4-4m4 4V4"
                        />
                    </svg>
                    <span>Export CSV</span>
                </button>
            </div>

            <div
                className="relative flex flex-col w-full h-full overflow-auto text-gray-700 bg-white shadow-md rounded-lg bg-clip-border">
                <table className="w-full table-auto text-left min-w-max border-collapse" style={{tableLayout: 'fixed'}}>
                    <thead>
                    <tr className="border-b border-slate-300 bg-slate-50">
                        <th className="p-4 text-sm font-normal leading-none text-slate-500 w-1/5">Images</th>
                        <th className="p-4 text-sm font-normal leading-none text-slate-500 w-2/5">Name</th>
                            <th className="p-4 text-sm font-normal leading-none text-slate-500 w-1/5">Price</th>
                            <th className="p-4 text-sm font-normal leading-none text-slate-500 w-1/5">Link</th>
                        </tr>
                    </thead>
                    <tbody>
                        {currentProducts.map((product, index) => (
                            <tr key={index} className="hover:bg-slate-50">
                                <td className="p-4 border-b border-slate-200 py-5">
                                    <div className="flex items-center justify-center">
                                        {/* Previous Image Button */}
                                        {product.product_img_urls && product.product_img_urls.length > 1 && (
                                            <button
                                                onClick={() =>
                                                    handlePreviousImage(index, product.product_img_urls.length)
                                                }
                                                className="text-gray-500 hover:text-gray-900"
                                            >
                                                &lt;
                                            </button>
                                        )}

                                        {/* Show the current image */}
                                        {product.product_img_urls && product.product_img_urls.length > 0 ? (
                                            <img
                                                src={product.product_img_urls[currentImageIndex[index]]}
                                                alt={product.product_name}
                                                className="w-16 h-16 object-cover rounded mx-2"
                                                onError={(e) => {
                                                    e.target.onerror = null; // Prevent infinite loop if placeholder fails
                                                    e.target.src = placeholderImage; // Fallback to placeholder image
                                                }}
                                            />
                                        ) : (
                                            <img
                                                src={placeholderImage} // Placeholder image if no image URL
                                                alt="Placeholder"
                                                className="w-16 h-16 object-cover rounded mx-2"
                                            />
                                        )}

                                        {/* Next Image Button */}
                                        {product.product_img_urls && product.product_img_urls.length > 1 && (
                                            <button
                                                onClick={() =>
                                                    handleNextImage(index, product.product_img_urls.length)
                                                }
                                                className="text-gray-500 hover:text-gray-900"
                                            >
                                                &gt;
                                            </button>
                                        )}
                                    </div>
                                </td>
                                <td className="p-4 border-b border-slate-200 py-5 overflow-hidden">
                                    <p
                                        className="block font-semibold text-sm text-slate-800"
                                        style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}
                                        title={product.product_name} // Tooltip to show full name on hover
                                    >
                                        {product.product_name}
                                    </p>
                                </td>
                                <td className="p-4 border-b border-slate-200 py-5">
                                    <p className="text-sm text-slate-500">
                                        {product.product_price ? `${product.product_price}` : 'Price not available'}
                                    </p>
                                </td>
                                <td className="p-4 border-b border-slate-200 py-5 overflow-hidden">
                                    <a
                                        href={product.link}
                                        className="text-blue-500 underline truncate"
                                        target="_blank"
                                        rel="noreferrer"
                                        style={{ display: 'inline-block', maxWidth: '100%', overflow: 'hidden', textOverflow: 'ellipsis' }}
                                    >
                                        View Product
                                    </a>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Pagination Component */}
            <Pagination
                totalPages={totalPages}
                currentPage={currentPage}
                onPageChange={setCurrentPage}
                totalItems={totalItems}
                itemsPerPage={itemsPerPage}
            />
        </div>
    );
};

export default ProductTable;
