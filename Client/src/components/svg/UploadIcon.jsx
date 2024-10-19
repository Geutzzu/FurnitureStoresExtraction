import React from "react";

const UploadIcon = ({ className }) => (
  <svg className={`${className}`}  xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      width="24"
      height="24"
      fill="none"
      stroke="currentColor"
    >
      <path d="M4 12l8-8 8 8" />
      <line x1="12" y1="4" x2="12" y2="20" />
      <rect x="4" y="24" width="16" height="0.1" rx="1" />
    </svg>
);

export default UploadIcon;
