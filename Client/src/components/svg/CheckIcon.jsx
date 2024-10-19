import React from "react";

const CheckIcon = ({ className }) => (
  <svg className={`text-green-500 ${className}`} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
    <path
      fillRule="evenodd"
      d="M10 18a8 8 0 100-16 8 8 0 000 16zm-1.5-8.9l4.8-4.9 1.4 1.5-6.2 6.3L5.5 9.1l1.4-1.4 1.6 1.6z"
      clipRule="evenodd"
    />
  </svg>
);

export default CheckIcon;