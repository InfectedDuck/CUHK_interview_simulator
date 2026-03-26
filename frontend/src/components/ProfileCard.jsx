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

      {profile.projects?.length > 0 && (
        <div className="profile-section">
          <h4>Projects</h4>
          {profile.projects.map((proj, i) => (
            <div key={i} className="project-item">
              <strong>{proj.name || "Unnamed Project"}</strong>
              {proj.description && <p>{proj.description}</p>}
              {proj.technologies?.length > 0 && (
                <div className="tags" style={{ marginTop: 4 }}>
                  {proj.technologies.map((t, j) => (
                    <span key={j} className="tag">{t}</span>
                  ))}
                </div>
              )}
              {proj.role && <p className="project-meta"><em>Role:</em> {proj.role}</p>}
              {proj.outcome && <p className="project-meta"><em>Outcome:</em> {proj.outcome}</p>}
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

      {profile.achievements?.length > 0 && (
        <div className="profile-section">
          <h4>Achievements</h4>
          <div className="tags">
            {profile.achievements.map((a, i) => (
              <span key={i} className="tag achievement">{a}</span>
            ))}
          </div>
        </div>
      )}

      {profile.interests?.length > 0 && (
        <div className="profile-section">
          <h4>Interests</h4>
          <div className="tags">
            {profile.interests.map((item, i) => (
              <span key={i} className="tag interest">{item}</span>
            ))}
          </div>
        </div>
      )}

      {profile.personality_traits?.length > 0 && (
        <div className="profile-section">
          <h4>Personality Traits</h4>
          <div className="tags">
            {profile.personality_traits.map((t, i) => (
              <span key={i} className="tag trait">{t}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
