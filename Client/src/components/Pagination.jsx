import React from 'react';

// this handles the pagination of the products table
const Pagination = ({ totalPages, currentPage, onPageChange, totalItems, itemsPerPage }) => {
  const startItem = (currentPage - 1) * itemsPerPage + 1;
  const endItem = Math.min(startItem + itemsPerPage - 1, totalItems);

  const handlePrevious = () => {
    if (currentPage > 1) {
      onPageChange(currentPage - 1);
    }
  };

  const handleNext = () => {
    if (currentPage < totalPages) {
      onPageChange(currentPage + 1);
    }
  };

  return (
    <div className="flex items-center justify-between mt-4">
      <span className="text-gray-700">
        {startItem}-{endItem} of {totalItems}
      </span>
      <div>
        { /* left button */}
        <button
          onClick={handlePrevious}
          disabled={currentPage === 1}
          className={`px-4 py-2 mr-2 text-white bg-darkGraphite rounded ${currentPage === 1 ? 'opacity-50 cursor-not-allowed' : 'hover:opacity-90'}`}
        >
          &lt;
        </button>
        { /* right button */}
        <button
          onClick={handleNext}
          disabled={currentPage === totalPages}
          className={`px-4 py-2 text-white bg-darkGraphite rounded ${currentPage === totalPages ? 'opacity-50 cursor-not-allowed' : 'hover:opacity-90'}`}
        >
          &gt;
        </button>
      </div>
    </div>
  );
};

export default Pagination;
