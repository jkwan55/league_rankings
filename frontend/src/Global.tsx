/* eslint-disable no-trailing-spaces */
/* eslint-disable @typescript-eslint/explicit-function-return-type */
/* eslint-disable @typescript-eslint/semi */
/* eslint-disable no-tabs */
/* eslint-disable @typescript-eslint/member-delimiter-style */
/* eslint-disable @typescript-eslint/indent */

import React, { useState, useEffect } from 'react';
import './search.css';

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
// interface Data {
// 	team_name: string;
// }

// interface Props {
//     data: Data[];
// 	weights: number[];
// }

const Global = () => {
    // const currentDate: Date = new Date();
    // const previousDate: Date = new Date();
    // previousDate.setMonth(previousDate.getMonth() - 6);
    // const [filteredData, setFilteredData] = useState<Data[]>([...data]);

	// useEffect(() => {
	// 	const betweenData: Data[] = filteredData.filter((stats: Data) => {
	// 		const dataDate: number = Date.parse(stats.start_date);
	// 		return dataDate >= previousDate.getTime() && dataDate <= currentDate.getTime();
	// 	});
	// 	setFilteredData(betweenData);
	// }, []);

	const [data, setData] = useState<string[]>([]);
	const [search, setSearch] = useState<string>('');
	const [amount, setAmount] = useState<number>(20);

	const fetchItems = async (amt?: number) => {
		const requestOptions = {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' }
			// body: JSON.stringify({ amount: amt })
		};
		if (amt != null) {
			Object.assign(requestOptions, { body: JSON.stringify({ amount: amt }) });
		}
		try {
			await fetch('http://ec2-54-193-47-8.us-west-1.compute.amazonaws.com:8000/league_rankings/global/', requestOptions)
				.then(async res => await res.json())
				.then(dataResult => {
					setData(dataResult.data);
				})
				.catch(err => { console.log(err); });
		} catch (error) {
			console.error('Error fetching items:', error);
			throw error;
		}
	}
	
	useEffect(() => {
		fetchItems().catch(err => { console.log(err) });
	}, []);

	const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setSearch(e.target.value);
    }

	const handleOnSubmit = (e: React.FormEvent<HTMLFormElement>) => {
		e.preventDefault();
		// eslint-disable-next-line @typescript-eslint/ban-ts-comment
		// @ts-expect-error
		setAmount(parseInt(e.target[0].value));
	}

	useEffect(() => {
		fetchItems(amount).catch(err => { console.log(err) });
	}, [amount])

    return (
        <div>
            <h2>Top teams that played within the last 6 months:</h2>
			<p>Currently not optimized for tournament tiers</p>
			{/* <div className='searchbar-area'> */}
			<form onSubmit={handleOnSubmit} className='searchbar-area'>
				<input className='searchbar' placeholder='list amount of top teams' 
					onChange={(e: React.ChangeEvent<HTMLInputElement>) => { handleSearchChange(e) }}
					value={search}
				></input>
				<button type='submit' className='button'>Enter</button>
			</form>
			{/* </div> */}
			<ul>{data.length > 0
				? data.map((item, id) => {
				return <ul key={id} className='ranks'>{id + 1}: {item}</ul> 
				}) 
				: 'no data or loading'
			}</ul>
        </div>
    )
}

export default Global;
