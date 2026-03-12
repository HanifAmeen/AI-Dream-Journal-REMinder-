import { useEffect, useState } from "react";
import "./profile.css";

export default function ProfilePage() {

  const storedUser = JSON.parse(localStorage.getItem("user"));

  const [profile, setProfile] = useState({
    username: "",
    email: "",
    dob: "",
    age: "",
    nationality: "",
    gender: "",
    star_sign: ""
  });

  // Load base user info
  useEffect(() => {
    if (storedUser) {
      setProfile(prev => ({
        ...prev,
        username: storedUser.username,
        email: storedUser.email
      }));
    }
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;

    setProfile({
      ...profile,
      [name]: value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    console.log("Saving profile:", profile);

    // later you will POST this to backend
  };

  return (
    <div className="profile-container">

      <h1 className="profile-title">Your Profile</h1>

      <form className="profile-form" onSubmit={handleSubmit}>

        <div className="profile-grid">

          <div className="form-group">
            <label>Name</label>
            <input
              type="text"
              value={profile.username}
              disabled
            />
          </div>

          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={profile.email}
              disabled
            />
          </div>

          <div className="form-group">
            <label>Date of Birth</label>
            <input
              type="date"
              name="dob"
              value={profile.dob}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label>Age</label>
            <input
              type="number"
              name="age"
              value={profile.age}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label>Nationality</label>
            <input
              type="text"
              name="nationality"
              value={profile.nationality}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label>Gender</label>
            <select
              name="gender"
              value={profile.gender}
              onChange={handleChange}
            >
              <option value="">Select</option>
              <option>Male</option>
              <option>Female</option>
              <option>Non-binary</option>
              <option>Prefer not to say</option>
            </select>
          </div>

          <div className="form-group">
            <label>Star Sign (optional)</label>
            <input
              type="text"
              name="star_sign"
              value={profile.star_sign}
              onChange={handleChange}
              placeholder="Aries, Pisces, etc."
            />
          </div>

        </div>

        <button className="save-profile">
          Save Profile
        </button>

      </form>

    </div>
  );
}