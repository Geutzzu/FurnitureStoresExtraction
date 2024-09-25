import React, { useState } from 'react';
import Pagination from './Pagination';

const ProductTable = ({ products = [] }) => {
    const [currentPage, setCurrentPage] = useState(1);
    const itemsPerPage = 5; // Set your items per page
    const totalItems = products.length;
    const totalPages = Math.ceil(totalItems / itemsPerPage);


    // Slice products for the current page
    const currentProducts = products.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

    return (
        <div className="max-w-[1280px] mx-auto pb-28">
            <div className="w-full flex justify-between items-center mb-3 mt-12 pl-3">
                <div>
                    <h3 className="text-lg font-semibold text-slate-800">Furniture Products extracted</h3>
                    <p className="text-slate-500">This is what I found !</p>
                </div>
            </div>

            <div className="relative flex flex-col w-full h-full overflow-scroll text-gray-700 bg-white shadow-md rounded-lg bg-clip-border">
                <table className="w-full text-left table-auto min-w-max">
                    <thead>
                    <tr className="border-b border-slate-300 bg-slate-50">
                        <th className="p-4 text-sm font-normal leading-none text-slate-500">Images</th>
                        <th className="p-4 text-sm font-normal leading-none text-slate-500">Name</th>
                        <th className="p-4 text-sm font-normal leading-none text-slate-500">Price</th>
                        <th className="p-4 text-sm font-normal leading-none text-slate-500">Link</th>

                    </tr>
                    </thead>
                    <tbody>
                    {currentProducts.map((product, index) => (
                            <tr key={index} className="hover:bg-slate-50">
                                <td className="p-4 border-b border-slate-200 py-5">
                                    <img src={product.image} alt={product.name} className="w-16 h-16 object-cover rounded" />
                                </td>
                                <td className="p-4 border-b border-slate-200 py-5">
                                    <p className="block font-semibold text-sm text-slate-800">{product.name}</p>
                                </td>
                                <td className="p-4 border-b border-slate-200 py-5">
                                    <p className="text-sm text-slate-500">${product.price}</p>
                                </td>
                                <td className="p-4 border-b border-slate-200 py-5">
                                    <a href={product.link}
                                       className="text-blue-500 underline" target="_blank" rel="noreferrer">View Product</a>
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
