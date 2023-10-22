/* eslint-disable no-trailing-spaces */
/* eslint-disable @typescript-eslint/explicit-function-return-type */
/* eslint-disable @typescript-eslint/semi */
/* eslint-disable no-tabs */
/* eslint-disable @typescript-eslint/member-delimiter-style */
/* eslint-disable @typescript-eslint/indent */

import React, { useState } from 'react';
import './search.css';

const Tournament = () => {
	const [data, setData] = useState<string[]>([]);
	const [search, setSearch] = useState<string>('');
	const [searchStage, setSearchStage] = useState<string>('');
	// const options = ['groups', 'knockouts', 'regular_season', 'playoffs', 'round_1', 'round_2', 'elim', 'promotion', 'regionals', 'play_in_groups', 'play_in_elim',
	// 	'promotion_series', 'regional_qualifier', 'regional_finals', 'bracket_stage', 'play_in_group', 'east','west']

	const fetchItems = async (tournamentId?: number | string, stageSlug?: string) => {
		const requestOptions = {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' }
			// body: JSON.stringify({ amount: amt })
		};
		if (tournamentId != null) {
			let slug = '';
			if (stageSlug != null) {
				slug = stageSlug;
			}
			Object.assign(requestOptions, { body: JSON.stringify({ tournament_id: tournamentId, stage: slug }) });
		}
		try {
			await fetch('http://ec2-54-193-47-8.us-west-1.compute.amazonaws.com:8000/league_rankings/tournament/', requestOptions)
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

	const handleSearchStageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setSearchStage(e.target.value);
    }

	const handleOnSubmit = (e: React.FormEvent<HTMLFormElement>) => {
		e.preventDefault();
		fetchItems(search, searchStage).catch(err => { console.log(err) });
	}

    return (
        <div>
            <h2>Top teams for specific tournament</h2>
			<p>Currently not optimized for tournament tiers</p>
			<p>Was going to create a drop down, but ran out of time</p>
			<p>Stage ex - Regular season : regular_season</p>
			{/* <div className='searchbar-area'> */}
			<form onSubmit={handleOnSubmit} className='searchbar-area'>
				<input className='searchbar' placeholder='Tournament ID' 
					onChange={(e: React.ChangeEvent<HTMLInputElement>) => { handleSearchChange(e) }}
					value={search}
				></input>
				<input className='searchbar' placeholder='Stage (string)' 
					onChange={(e: React.ChangeEvent<HTMLInputElement>) => { handleSearchStageChange(e) }}
					value={searchStage}
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

export default Tournament;
