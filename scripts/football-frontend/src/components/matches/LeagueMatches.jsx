// src/components/matches/LeagueMatches.jsx
import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import MatchCard from "./MatchCard";

const LeagueMatches = (props) => {
  // league from prop or URL
  const { leagueName } = useParams();
  const leagueFromUrl = leagueName ? decodeURIComponent(leagueName) : "";
  const league = props.league || leagueFromUrl;

  const [finishedMatches, setFinishedMatches] = useState([]);
  const [upcomingMatches, setUpcomingMatches] = useState([]);

  const [limit, setLimit] = useState(300); // big enough for a full season

  const [seasons, setSeasons] = useState([]);
  const [seasonFilter, setSeasonFilter] = useState("");

  const [loadingFinished, setLoadingFinished] = useState(false);
  const [loadingUpcoming, setLoadingUpcoming] = useState(false);

  const [errorFinished, setErrorFinished] = useState("");
  const [errorUpcoming, setErrorUpcoming] = useState("");

  const PAGE_SIZE = 5;

  // separate pagination for upcoming and finished
  const [upcomingPage, setUpcomingPage] = useState(0);
  const [finishedPage, setFinishedPage] = useState(0);

  // Fetch seasons 
  const fetchSeasons = async () => {
    if (!league) return;

    try {
      const params = new URLSearchParams();
      params.append("league", league);

      const res = await fetch(
        `http://127.0.0.1:5000/api/seasons?${params.toString()}`
      );
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      setSeasons(data || []);

      if (data && data.length > 0) {
        setSeasonFilter(String(data[0])); // latest season first
      } else {
        setSeasonFilter("");
      }
    } catch (err) {
      console.error(err);
    }
  };

  //  Fetch finished matches (with probs) 
  const fetchFinishedMatches = async () => {
    if (!league || !seasonFilter) return;

    setLoadingFinished(true);
    setErrorFinished("");

    try {
      const params = new URLSearchParams();
      params.append("limit", String(limit));
      params.append("league", league);
      params.append("season", seasonFilter.trim());

      const res = await fetch(
        `http://127.0.0.1:5000/api/matches?${params.toString()}`
      );
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();

      let normalized = data.map((m) => ({
        ...m,
        _dateObj: m.date ? new Date(m.date) : null,
      }));

      // finished = matches with date in the past
      const now = new Date();
      const finished = normalized.filter(
        (m) => m._dateObj && !isNaN(m._dateObj.getTime()) && m._dateObj < now
      );

      finished.sort((a, b) => a._dateObj - b._dateObj);

      if (!finished.length) {
        setErrorFinished(
          `No finished matches for ${league} in ${seasonFilter}.`
        );
      }

      setFinishedMatches(finished);
      setFinishedPage(0);
    } catch (err) {
      console.error(err);
      setErrorFinished(err.message || "Failed to load finished matches");
    } finally {
      setLoadingFinished(false);
    }
  };

  //  Fetch upcoming matches from STATS CSV 
  const fetchUpcomingMatches = async () => {
    if (!league || !seasonFilter) return;

    setLoadingUpcoming(true);
    setErrorUpcoming("");

    try {
      const params = new URLSearchParams();
      params.append("limit", "300");
      params.append("league", league);
      params.append("season", seasonFilter.trim());

      const res = await fetch(
        `http://127.0.0.1:5000/api/upcoming_matches?${params.toString()}`
      );
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();

      const normalized = data.map((m) => ({
        ...m,
        _dateObj: m.date ? new Date(m.date) : null,
      }));

      normalized.sort((a, b) => a._dateObj - b._dateObj);

      setUpcomingMatches(normalized);
      setUpcomingPage(0);

      if (!normalized.length) {
        setErrorUpcoming(
          `No upcoming matches for ${league} in season ${seasonFilter}.`
        );
      }
    } catch (err) {
      console.error(err);
      setErrorUpcoming(err.message || "Failed to load upcoming matches");
    } finally {
      setLoadingUpcoming(false);
    }
  };

  // Effects
  useEffect(() => {
    if (league) {
      fetchSeasons();
    } else {
      setSeasons([]);
      setSeasonFilter("");
      setFinishedMatches([]);
      setUpcomingMatches([]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [league]);

  useEffect(() => {
    if (league && seasonFilter) {
      fetchFinishedMatches();
      fetchUpcomingMatches();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [league, seasonFilter, limit]);

  // Pagination calculations 
  const upcomingTotalPages =
    upcomingMatches.length > 0
      ? Math.ceil(upcomingMatches.length / PAGE_SIZE)
      : 1;

  const finishedTotalPages =
    finishedMatches.length > 0
      ? Math.ceil(finishedMatches.length / PAGE_SIZE)
      : 1;

  const upcomingStart = upcomingPage * PAGE_SIZE;
  const upcomingSlice = upcomingMatches.slice(
    upcomingStart,
    upcomingStart + PAGE_SIZE
  );

  const finishedStart = finishedPage * PAGE_SIZE;
  const finishedSlice = finishedMatches.slice(
    finishedStart,
    finishedStart + PAGE_SIZE
  );

  const handleUpcomingPrev = () =>
    setUpcomingPage((p) => Math.max(p - 1, 0));
  const handleUpcomingNext = () =>
    setUpcomingPage((p) => Math.min(p + 1, upcomingTotalPages - 1));

  const handleFinishedPrev = () =>
    setFinishedPage((p) => Math.max(p - 1, 0));
  const handleFinishedNext = () =>
    setFinishedPage((p) => Math.min(p + 1, finishedTotalPages - 1));

  //  UI 
  if (!league) {
    return <p style={{ color: "white" }}>Select a league to see matches.</p>;
  }

  return (
    <div>
      {/* Header: league + season selector */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "0.75rem",
        }}
      >
        <h2 style={{ color: "white", margin: 0 }}>{league}</h2>

        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <label style={{ color: "white", fontSize: "0.9rem" }}>Season:</label>
          <select
            value={seasonFilter}
            onChange={(e) => setSeasonFilter(e.target.value)}
            className="season-select"
          >
            {seasons.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* UPCOMING SECTION – paginated */}
      <div style={{ marginBottom: "1rem" }}>
        <h3
          style={{ color: "white", marginBottom: "0.5rem", fontSize: "1rem" }}
        >
          Upcoming matches
        </h3>

        {loadingUpcoming && (
          <p style={{ color: "white", fontSize: "0.85rem" }}>Loading…</p>
        )}

        {!loadingUpcoming && errorUpcoming && (
          <p style={{ color: "white", fontSize: "0.85rem" }}>{errorUpcoming}</p>
        )}

        {upcomingSlice.length > 0 && (
          <>
            <div className="matches-grid">
              {upcomingSlice.map((match, idx) => (
                <MatchCard
                  key={match.fixture_id || `${match.date}-up-${upcomingStart + idx}`}
                  match={match}
                  index={upcomingStart + idx}
                />
              ))}
            </div>

            <div className="matches-pagination">
              <button
                onClick={handleUpcomingPrev}
                disabled={upcomingPage === 0}
              >
                Prev
              </button>
              <span>
                Page {upcomingPage + 1} / {upcomingTotalPages}
              </span>
              <button
                onClick={handleUpcomingNext}
                disabled={upcomingPage >= upcomingTotalPages - 1}
              >
                Next
              </button>
            </div>
          </>
        )}
      </div>

      {/* FINISHED SECTION – paginated */}
      <h3
        style={{
          color: "white",
          marginBottom: "0.5rem",
          fontSize: "1rem",
          marginTop: "0.5rem",
        }}
      >
        Finished matches
      </h3>

      {errorFinished && (
        <p style={{ color: "white", marginBottom: "0.5rem" }}>
          {errorFinished}
        </p>
      )}

      {loadingFinished && !finishedMatches.length && (
        <p style={{ color: "white" }}>Loading finished matches…</p>
      )}

      {finishedSlice.length > 0 && (
        <>
          <div className="matches-grid">
            {finishedSlice.map((match, idx) => (
              <MatchCard
                key={match.fixture_id || `${match.date}-fin-${finishedStart + idx}`}
                match={match}
                index={finishedStart + idx}
              />
            ))}
          </div>

          <div className="matches-pagination">
            <button
              onClick={handleFinishedPrev}
              disabled={finishedPage === 0}
            >
              Prev
            </button>
            <span>
              Page {finishedPage + 1} / {finishedTotalPages}
            </span>
            <button
              onClick={handleFinishedNext}
              disabled={finishedPage >= finishedTotalPages - 1}
            >
              Next
            </button>
          </div>
        </>
      )}

      {loadingFinished && finishedMatches.length > 0 && (
        <p style={{ color: "white", marginTop: "0.5rem" }}>Updating…</p>
      )}
    </div>
  );
};

export default LeagueMatches;
