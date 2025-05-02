import React from 'react'
import { useState, useEffect } from 'react';
import { useParams, useLocation, Redirect } from 'react-router-dom';
import {ReactComponent as Loader} from "../loader.svg"

const Recommender = (props) => {
    let [displayname, setDisplayName] = useState("")
    let [image, setImage] = useState("")

    // setup parameter map
    let params = new URLSearchParams(useLocation().search)
    let token = params.get("token")

    // redirectionare catre Spotify pentru autentificare
    const RedirectUrl = async () => {
        const response = await fetch("http://localhost:8000/api/url");
        const data = await response.json();
        // console.log(data)
        window.location.href = data["url"];

    }
    
    // get name from url
    // let {token} = useParams()

    useEffect(() => {
        getUser();
      }, []);


    let getUser = async () =>{
        // daca nu are token
        if(!token){
            return RedirectUrl();
        }
        const response = await fetch("https://api.spotify.com/v1/me",{headers:{
            Authorization: "Bearer " + token
        }});
        // daca ceva merge nasol cu token ul (cel mai probabil este expirat)
        if(!response.ok){
            return RedirectUrl();
        }
        const data = await response.json();
        setDisplayName(data["display_name"]);
        setImage(data["images"][0]["url"])
    }

  
    return (
    <div className='app-container'>
        <header>
            <h4><img className = "spotify-logo" src="https://cdn.iconscout.com/icon/premium/png-256-thumb/spotify-3856186-3201519.png?f=webp"/>Spotify Recommender</h4>
        </header>
        <AccountInfo image = {image} displayname = {displayname} />
        <RecommendOptions/>
    </div>
  )
}

const AccountInfo = (props) => {
    return (
        <div className='accountInfo'>
            <img src={props.image}/><text>Salut {props.displayname}!</text>
        </div>)
}

const RateButtons = (props) => {
    const [rating, setRating] = useState("")
    const [likeEnabled, setLikeEnabled] = useState(true)
    const [dislikeEnabled, setDislikeEnabled] = useState(true)

    useEffect(() => {
        setLikeEnabled(true)
        setDislikeEnabled(true)
    }, [props.song])


    const Like = async () => {
        setRating("like")
        const response = await fetch("http://localhost:8000/api/rate?user=" + props.user + "&song=" + props.song + "&rating=" + rating)
        if(!response.ok){
            console.error("Something went wrong")
            return
        }
        const data = await response.json()
        console.log(data)
        setDislikeEnabled(false)
        setLikeEnabled(false)
    }

    const Dislike = async() =>{
        setRating("dislike")
        const response = await fetch("http://localhost:8000/api/rate?user=" + props.user + "&song=" + props.song + "&rating=" + rating)
        if(!response.ok){
            console.error("Something went wrong")
            return
        }
        const data = await response.json()
        console.log(data)
        setDislikeEnabled(false)
        setLikeEnabled(false)
    }


    return(
        <div>
            {/* {(rating !=="like") ? <button onClick={Dislike} disabled={!dislikeEnabled}>Dislike</button> : <div></div>}
            {rating !=="dislike" ? <button onClick={Like} disabled={!likeEnabled}>Like</button> : <div></div>} */}
            <button onClick={Dislike} disabled={!dislikeEnabled} className='btn-dislike'>Dislike</button>
            <button onClick={Like} disabled={!likeEnabled} className='btn-like'>Like</button>
        </div>
    )
}

const RecommendOptions = () =>{

    const [genres, setGenres] = useState([])
    const [song, setSong] = useState()
    const [submitLoading, setSubmitLoading] = useState("Generare Recomandare")
    const [submitDisabled, setSubmitDisabled] = useState(false)
    const [refreshLoading, setRefreshLoading] = useState("Reimprospatare behavior")
    const [refreshDisabled, setRefreshDisabled] = useState(false)

    const [fieldGenuri, setFieldGenuri] = useState("any")
    const [boolManele, setBoolManele] = useState("true")

    // setup parameter map
    let params = new URLSearchParams(useLocation().search)
    let token = params.get("token")


    const getGenres = async () =>{
        const response = await fetch("http://localhost:8000/api/genres")
        const data = await response.json()
        setGenres(data["genres"])
    }

    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    const recommendSong = async () =>{
        setSubmitDisabled(true)
        const text = submitLoading
        setSubmitLoading(<Loader className="spinner"/>)
        const response = await fetch("http://localhost:8000/api/recommendation?token=" + token + "&gen=" + fieldGenuri + "&manele=" + boolManele)
        if(!response.ok){
            console.error("Nu am putut lua recomandare")
        }
        else{
            const data = await response.json()
            // console.log(data)
            setSong(data["song"])
        }
        setSubmitLoading(text)
        setSubmitDisabled(false)
    }

    const refreshBehavior = async () => {
        setRefreshDisabled(true)
        const text = refreshLoading
        setRefreshLoading(<Loader className = "spinner"/>)
        const response = await fetch("http://localhost:8000/api/behavior?token=" + token)
        if(!response.ok){
            console.error("A aparut o eroare")
        }
        else{
            console.log("Behavior actualizat cu success")
        }
        setRefreshLoading(text)
        setRefreshDisabled(false)
    }


    useEffect(()=>{
        getGenres()
    }, [])


    return(
        <div className='recommend-options'>
            <form>
                <p>Alege un gen muzical</p>
                <select name="genres" id='genres' value={fieldGenuri} onChange={(e) => setFieldGenuri(e.target.value)}>
                    <option value="any" >Oricare</option>
                    {/* populare meniu cu genurile din baza de date */}
                    {genres.map((option) => (
                        <option key={option} value={option}>
                            {option}
                        </option>
                    ))}
                </select>
                <p>
                <label for="manele">Manele in recomandari?</label>
                <input type='checkbox' name='manele' checked={boolManele} onChange={(e) => setBoolManele(e.target.checked)}></input>
                </p>
                <div>
                    <button className='refresh_behavior' type='button' onClick={refreshBehavior} disabled={refreshDisabled}>{refreshLoading}</button>
                    <button className='submit' type="button" onClick={recommendSong} disabled={submitDisabled}>{submitLoading}</button>
                </div>
            </form>
        <Song id = {song} user = {token}/>
        </div>
    )
}


const Song = (props) => {
    if(props.id){
    const url = "https://open.spotify.com/embed/track/" + props.id + "?utm_source=generator"
    return(
        <div className='song'>
            <iframe src={url} width="70%" height="152" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>
            <RateButtons song = {props.id} user={props.user}/>
        </div>
    )}
}



export default Recommender



