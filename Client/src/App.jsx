import { Outlet } from "react-router-dom";
import './index.css';

const App = () => {
  return (
    <div className="w-full">
      <Outlet />
    </div>
  );
};
export default App;