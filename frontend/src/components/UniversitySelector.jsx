const UNIVERSITIES = [
  "CUHK — The Chinese University of Hong Kong",
  "HKU — The University of Hong Kong",
  "HKUST — Hong Kong University of Science and Technology",
  "PolyU — The Hong Kong Polytechnic University",
  "CityU — City University of Hong Kong",
  "HKBU — Hong Kong Baptist University",
  "LingU — Lingnan University",
  "EdUHK — The Education University of Hong Kong",
];

export function UniversitySelector({ value, onChange }) {
  return (
    <div className="university-selector">
      <label htmlFor="university">Target University</label>
      <select
        id="university"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        <option value="">Select a university...</option>
        {UNIVERSITIES.map((u) => (
          <option key={u} value={u.split(" — ")[0]}>
            {u}
          </option>
        ))}
      </select>
    </div>
  );
}
