
import { Link } from 'react-router-dom';
import './NavBar.css';

const NavBar = () => {
    return(
        <div className='nav'>
            <div className='nav-child'>
                <ul>
                    <Link to="/">Global Ranks</Link>
                </ul>
                <ul>
                    <Link to="/team">Team Rankings</Link>
                </ul>
                <ul>
                    <Link to="/tournament">Tournament Rankings</Link>
                </ul>
                <ul>
                    <Link to="/globalall">Global Ranks (All Seasons)</Link>
                </ul>
                <ul>
                    <Link to="/teamall">Team Rankings (All Seasons)</Link>
                </ul>
            </div>
        </div>
    )

}

export default NavBar;