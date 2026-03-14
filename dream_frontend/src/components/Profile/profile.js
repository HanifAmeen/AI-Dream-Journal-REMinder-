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
    religion: ""
  });

  // Load base user info + saved profile
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const token = localStorage.getItem("token");
        if (!token) return;

        const res = await fetch("http://127.0.0.1:5000/get_profile", {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });

        const data = await res.json();

        if (data && Object.keys(data).length > 0) {
          setProfile(prev => ({
            ...prev,
            ...data
          }));
        }
      } catch (err) {
        console.error("Error loading profile:", err);
      }
    };

    // First load stored user info
    if (storedUser) {
      setProfile(prev => ({
        ...prev,
        username: storedUser.username,
        email: storedUser.email
      }));
    }

    // Then fetch saved profile from backend
    fetchProfile();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;

    let updatedProfile = {
      ...profile,
      [name]: value
    };

    // If DOB changes → calculate age automatically
    if (name === "dob" && value) {
      const birthDate = new Date(value);
      const today = new Date();

      let age = today.getFullYear() - birthDate.getFullYear();
      const monthDiff = today.getMonth() - birthDate.getMonth();

      if (
        monthDiff < 0 ||
        (monthDiff === 0 && today.getDate() < birthDate.getDate())
      ) {
        age--;
      }

      updatedProfile.age = age.toString();
    }

    setProfile(updatedProfile);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const token = localStorage.getItem("token");
      if (!token) {
        alert("No token found. Please login again.");
        return;
      }

      const res = await fetch("http://127.0.0.1:5000/update_profile", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(profile)
      });

      const data = await res.json();

      if (res.ok) {
        alert("Profile saved successfully!");
      } else {
        alert(`Error: ${data.error || "Failed to save profile"}`);
      }
    } catch (err) {
      console.error(err);
      alert("Failed to save profile. Please try again.");
    }
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
              readOnly
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
            <label>Religion</label>
            <input
              type="text"
              name="religion"
              value={profile.religion}
              onChange={handleChange}
              
            />
          </div>
        </div>

        <button className="save-profile" type="submit">
          Save Profile
        </button>
      </form>
    </div>
  );
}
