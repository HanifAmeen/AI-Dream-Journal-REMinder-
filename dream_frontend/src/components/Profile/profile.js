import { useEffect, useState } from "react";
import "./profile.css";

// ✅ FIXED → local backend
const API_URL = "http://localhost:5000";

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

  const [loading, setLoading] = useState(false);

  // ✅ LOAD PROFILE
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const token = localStorage.getItem("token");
        if (!token) return;

        const res = await fetch(`${API_URL}/get_profile`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });

        if (!res.ok) throw new Error("Failed to fetch profile");

        let data;
        try {
          data = await res.json();
        } catch {
          console.error("Invalid JSON (profile)");
          return;
        }

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

    if (storedUser) {
      setProfile(prev => ({
        ...prev,
        username: storedUser.username,
        email: storedUser.email
      }));
    }

    fetchProfile();
  }, []);

  // ✅ HANDLE INPUT
  const handleChange = (e) => {
    const { name, value } = e.target;

    let updatedProfile = {
      ...profile,
      [name]: value
    };

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

  // ✅ SAVE PROFILE
  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      setLoading(true);

      const token = localStorage.getItem("token");
      if (!token) {
        alert("No token found. Please login again.");
        return;
      }

      const res = await fetch(`${API_URL}/update_profile`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(profile)
      });

      let data;
      try {
        data = await res.json();
      } catch {
        alert("Invalid server response");
        return;
      }

      if (res.ok) {
        alert("Profile saved successfully!");
      } else {
        alert(`Error: ${data.error || "Failed to save profile"}`);
      }
    } catch (err) {
      console.error(err);
      alert("Failed to save profile.");
    } finally {
      setLoading(false);
    }
  };

  // ✅ DELETE ACCOUNT
  const handleDeleteAccount = async () => {
    const confirmDelete = window.confirm(
      "Are you sure you want to delete your account? This cannot be undone."
    );

    if (!confirmDelete) return;

    try {
      setLoading(true);

      const token = localStorage.getItem("token");

      const res = await fetch(`${API_URL}/delete_account`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      let data;
      try {
        data = await res.json();
      } catch {
        alert("Invalid server response");
        return;
      }

      if (res.ok) {
        alert("Account deleted successfully");

        localStorage.removeItem("token");
        localStorage.removeItem("user");
        localStorage.removeItem("conversation_id");

        window.location.href = "/login";
      } else {
        alert(data.error || "Failed to delete account");
      }
    } catch (err) {
      console.error(err);
      alert("Error deleting account");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="profile-container">
      <h1 className="profile-title">Your Profile</h1>

      <form className="profile-form" onSubmit={handleSubmit}>
        <div className="profile-grid">

          <div className="form-group">
            <label>Name</label>
            <input type="text" value={profile.username} disabled />
          </div>

          <div className="form-group">
            <label>Email</label>
            <input type="email" value={profile.email} disabled />
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
            <input type="number" value={profile.age} readOnly />
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

        <button className="save-profile" type="submit" disabled={loading}>
          {loading ? "Saving..." : "Save Profile"}
        </button>
      </form>

      <div style={{ marginTop: "30px", textAlign: "center" }}>
        <button
          onClick={handleDeleteAccount}
          style={{
            background: "#ff4d4f",
            color: "white",
            border: "none",
            padding: "12px 20px",
            borderRadius: "8px",
            cursor: "pointer",
            fontWeight: "bold"
          }}
        >
          Delete Account
        </button>
      </div>
    </div>
  );
}