import React, { useEffect, useState } from 'react';
import Pagination from './Pagination';
import placeholderImage from '../assets/placeholder-image.png'; // Add a placeholder image
import CloseIcon from "./svg/CloseIcon.jsx";
import DownloadIcon from "./svg/DownloadIcon.jsx";



const ProductTable = ({ products = [], onClearClick, isLoading }) => {
    const [currentPage, setCurrentPage] = useState(1);
    const itemsPerPage = 5; // set your items per page
    const totalItems = products.length;
    const totalPages = Math.ceil(totalItems / itemsPerPage);

    // state to store the current image index for each product
    const [currentImageIndex, setCurrentImageIndex] = useState({});

    // slice products for the current page
    const currentProducts = products.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

    // initialize image index for each product
    useEffect(() => {
        const initialImageIndexes = {};
        products.forEach((product, index) => {
            initialImageIndexes[index] = 0; // set first image as default for each product
        });
        setCurrentImageIndex(initialImageIndexes);
    }, [products]);

    // handle next image click - they will not work while products are being added to this table
    const handleNextImage = (productIndex, totalImages) => {
        setCurrentImageIndex((prevIndexes) => ({
            ...prevIndexes,
            [productIndex]: (prevIndexes[productIndex] + 1) % totalImages,
        }));
    };

    // handle previous image click - they will not work while products are being added to this table ( to fix this I would need to not rewrite all the results and indexes on each new product )
    const handlePreviousImage = (productIndex, totalImages) => {
        setCurrentImageIndex((prevIndexes) => ({
            ...prevIndexes,
            [productIndex]: (prevIndexes[productIndex] - 1 + totalImages) % totalImages,
        }));
    };

    useEffect(() => {
        console.log('Updated Products in ProductTable: ', products);
    }, [products]);

    // function to export CSV
    const exportToCSV = () => {
          // map the products array to create a cleaner CSV data array
          const csvData = products.map(product => ({
            Name: product.product_name || 'Name not available',
            Price: product.product_price || 'Price not available',
            Link: product.link
          }));

          const csvRows = [
                ['Name', 'Price', 'Link'], // CSV Header

                ...csvData.map(row => {
                  const name = String(row.Name)
                    .replace(/,/g, ' ') // replace commas with spaces
                    .replace(/\n+/g, ' ') // remove newlines and replace them with spaces

                  let price = String(row.Price)
                    .replace(/,/g, '.') // replace commas with dots for numerical formatting
                    .replace(/\s+/g, ' ') // replace all sequences of spaces/newlines with a single space
                    .trim();

                  const link = row.Link;
                  return [name, price, link];
                })
      ];

      const csvContent = csvRows.map(row => row.join(',')).join('\n');

      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.setAttribute('download', 'products.csv');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    };


    return (
        <div className="max-w-[1280px] mx-auto pb-28 ">
            <div className="w-full flex justify-between items-center mb-3 mt-12 pl-3">
                <div>
                    <h3 className="text-lg font-semibold text-slate-800">Furniture Products extracted</h3>
                    <p className="text-slate-500">This is what I found!</p>
                </div>

                <div className={"flex space-x-4"}>
                    {/* export to CSV Button */}
                <button
                    className="flex items-center space-x-2 bg-darkGraphite hover:opacity-90 text-white font-bold py-2 px-4 rounded"
                    onClick={() => exportToCSV(products)}
                >
                    {/* SVG Icon for Download */}
                    <DownloadIcon className="w-6 h-6"/>
                    <span>Export CSV</span>
                </button>
                {/* clear table button  */}
                {!isLoading && (
                    <button
                    className="flex items-center space-x-2 bg-darkGraphite hover:opacity-90 text-white font-bold py-2 px-4 rounded"
                    onClick={onClearClick}
                >
                    {/* SVG Icon for Clear */}
                    <CloseIcon className="w-6 h-6"/>
                    <span>Clear</span>
                </button> )}
                </div>
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
                                        {/* previous Image Button */}
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

                                        {/* show the current image */}
                                        {product.product_img_urls && product.product_img_urls.length > 0 ? (
                                            <img
                                                src={product.product_img_urls[currentImageIndex[index]]}
                                                alt={product.product_name}
                                                className="w-16 h-16 object-cover rounded mx-2"
                                                onError={(e) => {
                                                    e.target.onerror = null; // prevent infinite loop if placeholder fails
                                                    e.target.src = placeholderImage; // fallback to placeholder image
                                                }}
                                            />
                                        ) : (
                                            <img
                                                src={placeholderImage} // placeholder image if no image URL
                                                alt="Placeholder"
                                                className="w-16 h-16 object-cover rounded mx-2"
                                            />
                                        )}

                                        {/* next Image Button */}
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
                                        title={product.product_name}
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
                                        className="text-slateGray underline truncate"
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

            {/* pagination Component */}
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
