/* eslint-disable @typescript-eslint/explicit-function-return-type */
/* eslint-disable @typescript-eslint/semi */
/* eslint-disable no-tabs */
/* eslint-disable @typescript-eslint/member-delimiter-style */
/* eslint-disable @typescript-eslint/indent */
import { Routes, Route, BrowserRouter as Router } from 'react-router-dom';
import Global from '@/Global';
import Tournament from '@/Tournament';
import Team from '@/Team';
import TeamAllTime from '@/TeamAllTime';
import GlobalAllTime from '@/GlobalAllTime';
import NavBar from '@/NavBar';

// interface Data {
// 	gold_10: number;
// 	gold_10_count: number;
// 	gold_20: number;
// 	gold_20_count: number;
// 	lost_count: number;
// 	lost_time: number;
// 	player_id: number;
// 	player_name: string;
// 	stage_slug: string;
// 	start_date: string;
// 	stat_id: number;
// 	tournament_id: number;
// 	tower_delta_10: number;
// 	tower_delta_10_count: number;
// 	tower_delta_20: number;
// 	tower_delta_20_count: number;
// 	win_count: number;
// 	win_time: number;
//     team_id: number;
//     role: string;
//     team_name: string;
// }

function App () {
	// const [data, setData] = useState<Data[]>([]);

	// for frontend computation
	// weights got from linear regression model from backend
	// modeled based on lcs_summer_2022 regular season
	// hardcoded due to lack of time
	// [0] -> 'AVG_GOLD_10_WEIGHT'
	// [1] -> 'AVG_GOLD_20_WEIGHT'
	// [2] -> 'AVG_TOWER_DELTA_10_WEIGHT'
	// [3] -> 'AVG_TOWER_DELTA_20_WEIGHT'
	// [4] -> 'WIN_RATE_WEIGHT'
	// [5] -> 'AVG_WIN_TIME_WEIGHT'
	// [6] -> 'AVG_LOST_TIME_WEIGHT'
	// const weights: number[] = [60.850482067668835, -81.86179372351509, 22.915557140713318, 25.515510378538025,
	// 	-9.376862747866605, -4.006092027320668, 2.1338514352977596];

	// useEffect(() => {
	// 	const fetchItems = async () => {
	// 		const requestOptions = {
	// 			method: 'GET',
	// 			headers: { 'Content-Type': 'application/json' }
	// 			// body: JSON.stringify({ userName:'myUserName' })
	// 		};
	// 		try {
	// 			await fetch('http://localhost:8000/league_rankings/data/', requestOptions)
	// 				.then(async res => await res.json())
	// 				.then(data => {
	// 					const temp: Data[] = [...data.data];
	// 					temp.sort((obj1, obj2) => { return Date.parse(obj1.start_date) - (Date.parse(obj2.start_date)) });
	// 					setData(temp);
	// 				})
	// 				.catch(err => { console.log(err); });
	// 		} catch (error) {
	// 			console.error('Error fetching items:', error);
	// 			throw error;
	// 		}
	// 	}
	// 	fetchItems().catch(err => { console.log(err) });
	// }, []);

	return (
		<div>
			<Router>
				<NavBar />
				<Routes>
					<Route path='/' element={<Global />} />
					<Route path='/team' element={<Team />} />
					<Route path='/tournament' element={<Tournament />} />
					<Route path='/teamall' element={<TeamAllTime />} />
					<Route path='/globalall' element={<GlobalAllTime />} />
				</Routes>
			</Router>
		</div>
	)
}

export default App
