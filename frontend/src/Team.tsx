/* eslint-disable no-trailing-spaces */
/* eslint-disable @typescript-eslint/explicit-function-return-type */
/* eslint-disable @typescript-eslint/semi */
/* eslint-disable no-tabs */
/* eslint-disable @typescript-eslint/member-delimiter-style */
/* eslint-disable @typescript-eslint/indent */

import React, { useState, useEffect } from 'react';
import './search.css';

const Team = () => {
	const [data, setData] = useState<string[]>([]);
	const [search, setSearch] = useState<string>('');
	const [teamArray, setTeamArray] = useState<string[]>([]);

	const fetchItems = async (teamIds: string[]) => {
		const requestOptions = {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' }
			// body: JSON.stringify({ amount: amt })
		};
		if (teamIds != null) {
			Object.assign(requestOptions, { body: JSON.stringify({ team_ids: teamIds }) });
		} else {
			console.log('missing team ids');
			return;
		}
		try {
			await fetch('http://ec2-54-193-47-8.us-west-1.compute.amazonaws.com:8000/league_rankings/team/', requestOptions)
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

	const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setSearch(e.target.value);
    }

	const handleOnSubmit = (e: React.FormEvent<HTMLFormElement>) => {
		e.preventDefault();
		setTeamArray(search.replace(/\s/g, '').split(','));
	}

	useEffect(() => {
		fetchItems(teamArray).catch(err => { console.log(err) });
	}, [teamArray])

    return (
        <div>
            <h2>Selected Top teams that played within the last 6 months:</h2>
			<p>Currently not optimized for tournament tiers</p>
			<p>Was going to create a drop down, but ran out of time</p>
			<p>Please use team_id comma separated</p>
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

export default Team;
