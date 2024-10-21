import { Outlet } from "react-router-dom";
import './index.css';


///  main app component - contains only the outlet
const App = () => {
  return (
    <div className="w-full">
      <Outlet />
    </div>
  );
};
export default App;