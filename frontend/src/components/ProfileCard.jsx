export function ProfileCard({ profile }) {
  if (!profile) return null;

  return (
    <div className="profile-card">
      <h3>Your Profile</h3>

      {profile.education && (
        <div className="profile-section">
          <h4>Education</h4>
          <p>
            {profile.education.level && <span>{profile.education.level} </span>}
            {profile.education.institution && <span>at {profile.education.institution} </span>}
            {profile.education.major && <span>— {profile.education.major}</span>}
            {profile.education.gpa && <span> (GPA: {profile.education.gpa})</span>}
          </p>
        </div>
      )}

      {profile.skills?.length > 0 && (
        <div className="profile-section">
          <h4>Skills</h4>
          <div className="tags">
            {profile.skills.map((skill, i) => (
              <span key={i} className="tag">{skill}</span>
            ))}
          </div>
        </div>
      )}

      {profile.experience?.length > 0 && (
        <div className="profile-section">
          <h4>Experience</h4>
          {profile.experience.map((exp, i) => (
            <div key={i} className="experience-item">
              <strong>{exp.title}</strong>
              {exp.organization && <span> at {exp.organization}</span>}
              {exp.description && <p>{exp.description}</p>}
            </div>
          ))}
        </div>
      )}

      {profile.goals && (
        <div className="profile-section">
          <h4>Goals</h4>
          <p>{profile.goals}</p>
        </div>
      )}

      {profile.target_universities?.length > 0 && (
        <div className="profile-section">
          <h4>Target Universities</h4>
          <div className="tags">
            {profile.target_universities.map((u, i) => (
              <span key={i} className="tag university">{u}</span>
            ))}
          </div>
        </div>
      )}

      {profile.target_programs?.length > 0 && (
        <div className="profile-section">
          <h4>Target Programs</h4>
          <div className="tags">
            {profile.target_programs.map((p, i) => (
              <span key={i} className="tag program">{p}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
