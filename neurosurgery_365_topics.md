# Neurosurgery / Neurology Practice Topic Calendar (365)

**One topic per day → one research digest upload. Never batch-upload multiple calendar topics on the same day.**

- **Source of truth:** `council_output/neurosurgery_365_calendar.json`
- **Compiled from:** `neurosurgery_365_calendar.json`
- **Day 1:** `2026-10-02` (Asia/Karachi civil date)
- **Day 365:** `2027-10-01`
- **Grok-authenticated entries:** 365/365
- **Uploads per day:** `1`

## Dating rule

Day 1 = 2026-10-02 (PKT / Asia/Karachi calendar date). Day N maps to ANCHOR_DATE + (N-1) days through 2027-10-01. Exactly ONE topic per day; daily pipeline publishes ONE digest/upload.

For date D, day_index = (D - 2026-10-02).days + 1. Publish exactly ONE research digest for that single topic.

```text
day_index = (PKT_today - 2026-10-02).days + 1
topic     = calendar.topics[day_index - 1]   # exactly one
publish   = ONE WordPress post / ONE council_output/daily_news_YYYYMMDD.md
```

## Domain counts

| Domain | Topics |
|---|---:|
| Cerebrovascular | 46 |
| Spine | 45 |
| Brain tumors | 44 |
| Functional | 30 |
| Trauma | 30 |
| Pediatric | 25 |
| Critical care | 20 |
| Ethics / guidelines | 20 |
| Hydrocephalus / CSF | 20 |
| Imaging / diagnostics | 20 |
| Infection / inflammation | 20 |
| Neuro-oncology medical | 15 |
| Peripheral nerve | 15 |
| Rehabilitation / outcomes | 15 |
| **Total** | **365** |

## How the daily job uses this

1. GitHub Action `neuro-daily-news.yml` runs `daily_neuro_news.py` once per day.
2. `topic_of_the_day.get_today_topic()` resolves **exactly one** calendar entry for today's PKT date.
3. Optional RSS feeds may supply a **single** best-match hint; if weak, Grok writes a research brief on the calendar topic alone.
4. Pipeline publishes **one** post only (`MAX_UPLOADS_PER_DAY = 1`).

Regenerate / re-authenticate:

```bash
python build_365_seed_calendar.py
python grok_authenticate_calendar.py --batch-size 35   # resumable
python compile_365_markdown.py
python topic_of_the_day.py   # prints today's single topic
```

## Sample week 1 (days 1–7)

| Day | Date | Domain | Topic |
|---:|---|---|---|
| 1 | 2026-10-02 | Brain tumors | Glioblastoma extent of resection and survival |
| 2 | 2026-10-03 | Brain tumors | IDH-mutant glioma surgical timing |
| 3 | 2026-10-04 | Brain tumors | Awake craniotomy language mapping updates |
| 4 | 2026-10-05 | Brain tumors | Meningioma Simpson grade in the MRI era |
| 5 | 2026-10-06 | Brain tumors | Convexity vs skull-base meningioma decision trees |
| 6 | 2026-10-07 | Brain tumors | Brain metastases: surgery vs SRS selection |
| 7 | 2026-10-08 | Brain tumors | Leptomeningeal disease neurosurgical roles |

### Day 1 detail

- **News angle:** Digest recent evidence on maximal safe resection, 5-ALA/fluorescence guidance, and how residual volume relates to survival endpoints in GBM.
- **Keywords:** `glioblastoma extent of resection 5-ALA residual volume survival`
- **Practice relevance:** Guides how aggressively to pursue cytoreduction while protecting neurologic function.

## Sample mid-year (days 180–186)

| Day | Date | Domain | Topic |
|---:|---|---|---|
| 180 | 2027-03-30 | Functional | DBS for dystonia |
| 181 | 2027-03-31 | Functional | Psychiatric neurosurgery ethics today |
| 182 | 2027-04-01 | Functional | Spasticity SDR in cerebral palsy |
| 183 | 2027-04-02 | Functional | Motor cortex stimulation for pain |
| 184 | 2027-04-03 | Functional | Peripheral nerve stimulation advances |
| 185 | 2027-04-04 | Functional | Asleep vs awake DBS techniques |
| 186 | 2027-04-05 | Functional | DBS hardware infection management |

## Final week (days 359–365)

| Day | Date | Domain | Topic |
|---:|---|---|---|
| 359 | 2027-09-25 | Ethics / guidelines | Do-not-escalate orders in neuro ICU clarity |
| 360 | 2027-09-26 | Ethics / guidelines | Trainee autonomy graded responsibility |
| 361 | 2027-09-27 | Ethics / guidelines | Religious and cultural end-of-life sensitivities |
| 362 | 2027-09-28 | Ethics / guidelines | Incidental germline findings in tumor NGS |
| 363 | 2027-09-29 | Ethics / guidelines | Industry-sponsored trial enrollment counseling |
| 364 | 2027-09-30 | Ethics / guidelines | Documentation standards for medicolegal resilience |
| 365 | 2027-10-01 | Ethics / guidelines | One-topic daily public education ethics |

## Domain overview (titles only)

### Cerebrovascular (46)

- D037 (2026-11-07): Brainstem cavernoma surgery thresholds
- D046 (2026-11-16): Unruptured aneurysm PHASES/UIATS counseling
- D047 (2026-11-17): ISAT/BRAT legacy versus flow-diversion era
- D048 (2026-11-18): Aneurysmal SAH antifibrinolytic timing
- D049 (2026-11-19): Delayed cerebral ischemia after SAH
- D050 (2026-11-20): Flow diverters for complex aneurysms
- D051 (2026-11-21): WEB and intrasaccular device update
- D052 (2026-11-22): AVM ARUBA aftermath and case selection
- D053 (2026-11-23): Spetzler-Martin grade surgical planning
- D054 (2026-11-24): Dural AV fistula Cognard/Borden management
- D055 (2026-11-25): ICH surgical trial updates (ENRICH and beyond)
- D056 (2026-11-26): Posterior fossa ICH decompression thresholds
- D057 (2026-11-27): EVT for large-core infarcts
- D058 (2026-11-28): Basilar artery occlusion EVT
- D059 (2026-11-29): Carotid stenosis: CEA versus CAS versus TCAR
- D060 (2026-11-30): Moyamoya revascularization indications
- D061 (2026-12-01): Cavernous malformation family counseling
- D062 (2026-12-02): Mycotic aneurysm management
- D063 (2026-12-03): Blister aneurysm strategies
- D064 (2026-12-04): Giant aneurysm bypass and trapping
- D065 (2026-12-05): CVST neurosurgical adjuncts
- D066 (2026-12-06): Perimesencephalic versus aneurysmal SAH workup
- D067 (2026-12-07): Antiplatelet management around aneurysm treatment
- D068 (2026-12-08): Spinal AVMs and dural fistulas
- D069 (2026-12-09): Intraoperative aneurysm rupture drills
- D070 (2026-12-10): Hunt-Hess and WFNS grading communication
- D071 (2026-12-11): Blood pressure targets after EVT
- D072 (2026-12-12): Secondary stroke prevention after aneurysm securement
- D073 (2026-12-13): Pediatric aneurysm peculiarities
- D074 (2026-12-14): Traumatic aneurysm after penetrating injury
- D075 (2026-12-15): Reversible cerebral vasoconstriction pitfalls
- D076 (2026-12-16): Subclavian steal and vertebral interventions
- D077 (2026-12-17): Intracranial atherosclerosis angioplasty/stent
- D078 (2026-12-18): Family screening after aneurysmal SAH
- D079 (2026-12-19): Pregnancy and cerebrovascular emergencies
- D080 (2026-12-20): Tele-stroke networks for EVT triage
- D081 (2026-12-21): Hematoma expansion predictors in ICH
- D082 (2026-12-22): Middle meningeal artery embolization for cSDH
- D083 (2026-12-23): Chronic subdural: twist-drill vs burr-hole vs craniotomy
- D084 (2026-12-24): Acute SDH surgical thresholds
- D085 (2026-12-25): EDH: lucid interval and OR timing
- D086 (2026-12-26): Hypertensive basal ganglia ICH medical first
- D087 (2026-12-27): Anticoagulant-associated ICH reversal
- D088 (2026-12-28): Vasospasm prophylaxis nimodipine adherence
- D089 (2026-12-29): External ventricular drain infection bundles
- D090 (2026-12-30): Cognitive outcomes after SAH

### Spine (45)

- D091 (2026-12-31): Lumbar disc herniation: when to operate
- D092 (2027-01-01): Cauda equina syndrome time-to-decompress
- D093 (2027-01-02): Cervical myelopathy natural history
- D094 (2027-01-03): ACDF vs cervical disc arthroplasty
- D095 (2027-01-04): Laminoplasty vs laminectomy-fusion for CSM
- D096 (2027-01-05): Lumbar stenosis MIS decompression
- D097 (2027-01-06): Degenerative spondylolisthesis fusion debate
- D098 (2027-01-07): Adult spinal deformity alignment goals
- D099 (2027-01-08): Proximal junctional kyphosis prevention
- D100 (2027-01-09): Thoracolumbar trauma AO classification surgery
- D101 (2027-01-10): Central cord syndrome surgical timing
- D102 (2027-01-11): Odontoid fracture elderly management
- D103 (2027-01-12): Hangman fracture operative criteria
- D104 (2027-01-13): Spinal epidural abscess urgency
- D105 (2027-01-14): Pyogenic spondylodiscitis surgical indications
- D106 (2027-01-15): Spinal tuberculosis: Hong Kong procedure vs modern debridement
- D107 (2027-01-16): Osteoporotic vertebral compression fractures
- D108 (2027-01-17): Sacroiliac joint pain versus lumbar pathology
- D109 (2027-01-18): Adjacent segment disease after fusion
- D110 (2027-01-19): Spinal cord stimulation for failed back surgery syndrome
- D111 (2027-01-20): Intraoperative neuromonitoring in spinal deformity
- D112 (2027-01-21): Pedicle screw navigation and robotics
- D113 (2027-01-22): Endoscopic lumbar discectomy learning curve
- D114 (2027-01-23): Cervical facet dislocation reduction
- D115 (2027-01-24): DISH-related spine trauma
- D116 (2027-01-25): Ankylosing spondylitis spine fracture care
- D117 (2027-01-26): Thoracic disc herniation: rare but cord-threatening
- D118 (2027-01-27): Lumbar synovial cyst management
- D119 (2027-01-28): Spinal meningioma: posterior approach outcomes
- D120 (2027-01-29): Metastatic spinal cord compression (MSCC)
- D121 (2027-01-30): Primary spine bone tumors: Enneking and WBB staging
- D122 (2027-01-31): Postoperative spinal epidural hematoma vigilance
- D123 (2027-02-01): Wound infection after instrumented fusion
- D124 (2027-02-02): BMP and biologics in spinal fusion
- D125 (2027-02-03): Opioid stewardship after spine surgery
- D126 (2027-02-04): Return-to-work after lumbar discectomy
- D127 (2027-02-05): Cervical radiculopathy: nonoperative care versus ACDF
- D128 (2027-02-06): Tarlov cysts: when to leave alone
- D129 (2027-02-07): Spinal arachnoid cyst and arachnoid web myelopathy
- D130 (2027-02-08): Pediatric scoliosis surgical timing
- D131 (2027-02-09): Neuromuscular scoliosis perioperative risk
- D132 (2027-02-10): Flatback syndrome revision strategies
- D133 (2027-02-11): Intraoperative vascular injury in lumbar surgery
- D134 (2027-02-12): Awake spine surgery under spinal anesthesia
- D135 (2027-02-13): Value-based spine care and low-value fusion

### Brain tumors (44)

- D001 (2026-10-02): Glioblastoma extent of resection and survival
- D002 (2026-10-03): IDH-mutant glioma surgical timing
- D003 (2026-10-04): Awake craniotomy language mapping updates
- D004 (2026-10-05): Meningioma Simpson grade in the MRI era
- D005 (2026-10-06): Convexity vs skull-base meningioma decision trees
- D006 (2026-10-07): Brain metastases: surgery vs SRS selection
- D007 (2026-10-08): Leptomeningeal disease neurosurgical roles
- D008 (2026-10-09): Pituitary adenoma endoscopic endonasal outcomes
- D009 (2026-10-10): Cushing disease: remission after TSA
- D010 (2026-10-11): Acromegaly surgical remission markers
- D011 (2026-10-12): Craniopharyngioma hypothalamic-sparing strategies
- D012 (2026-10-13): Vestibular schwannoma: wait-scan vs intervene
- D013 (2026-10-14): Insular glioma approach corridors
- D014 (2026-10-15): Intraoperative MRI and ultrasound for glioma
- D015 (2026-10-16): Fluorescence-guided resection beyond 5-ALA
- D016 (2026-10-17): Primary CNS lymphoma: biopsy first principles
- D017 (2026-10-18): Pineal region tumor biopsy vs resection
- D018 (2026-10-19): Intraventricular tumors and hydrocephalus
- D019 (2026-10-20): Recurrent GBM reoperation criteria
- D020 (2026-10-21): Molecular neuropathology for the operating surgeon
- D021 (2026-10-22): Laser interstitial thermal therapy (LITT) for tumors
- D022 (2026-10-23): Intraoperative neuromonitoring in tumor surgery
- D023 (2026-10-24): Hemangioblastoma and VHL counseling
- D024 (2026-10-25): Chordoma and chondrosarcoma skull base
- D025 (2026-10-26): Metastatic spine vs intracranial MDT sequencing
- D026 (2026-10-27): Seizure control after glioma resection
- D027 (2026-10-28): Elderly GBM: surgery vs biopsy-first
- D028 (2026-10-29): Optic pathway glioma observation thresholds
- D029 (2026-10-30): Dural-based mets mimicking meningioma
- D030 (2026-10-31): Thalamic glioma biopsy strategies
- D031 (2026-11-01): Cerebellar metastasis surgical indications
- D032 (2026-11-02): Tubular/minimally invasive tumor corridors
- D033 (2026-11-03): Second-look surgery after neoadjuvant therapy
- D034 (2026-11-04): Intraoperative frozen section limits
- D035 (2026-11-05): Radiation necrosis vs recurrence imaging
- D036 (2026-11-06): Venous sinus meningioma reconstruction
- D038 (2026-11-08): Incidental brain lesion counseling ethics
- D039 (2026-11-09): Neurocognitive outcomes after tumor surgery
- D040 (2026-11-10): Pediatric medulloblastoma risk stratification
- D041 (2026-11-11): Ependymoma: gross-total resection imperative
- D042 (2026-11-12): Primary intramedullary spinal cord tumors
- D043 (2026-11-13): Leptomeningeal disease and shunt decisions
- D044 (2026-11-14): Tumor-related epilepsy surgery adjuncts
- D045 (2026-11-15): ERAS pathways in cranial oncology

### Functional (30)

- D166 (2027-03-16): DBS for Parkinson disease patient selection
- D167 (2027-03-17): STN versus GPi DBS trade-offs
- D168 (2027-03-18): DBS for essential tremor
- D169 (2027-03-19): MR-guided focused ultrasound thalamotomy
- D170 (2027-03-20): Epilepsy surgery after failed AEDs
- D171 (2027-03-21): Temporal lobectomy versus laser ablation
- D172 (2027-03-22): SEEG-guided neuromodulation for epilepsy
- D173 (2027-03-23): Vagus nerve stimulation practical outcomes
- D174 (2027-03-24): Hemispherectomy and hemispherotomy selection
- D175 (2027-03-25): Trigeminal neuralgia: MVD versus rhizotomy versus SRS
- D176 (2027-03-26): Glossopharyngeal neuralgia recognition
- D177 (2027-03-27): Hemifacial spasm MVD outcomes
- D178 (2027-03-28): Occipital nerve stimulation for headache
- D179 (2027-03-29): Intrathecal drug delivery for spasticity/pain
- D180 (2027-03-30): DBS for dystonia
- D181 (2027-03-31): Psychiatric neurosurgery ethics today
- D182 (2027-04-01): Spasticity SDR in cerebral palsy
- D183 (2027-04-02): Motor cortex stimulation for pain
- D184 (2027-04-03): Peripheral nerve stimulation advances
- D185 (2027-04-04): Asleep vs awake DBS techniques
- D186 (2027-04-05): DBS hardware infection management
- D187 (2027-04-06): Epilepsy diet therapies adjunct to surgery
- D188 (2027-04-07): Stereo-EEG complications and yield
- D189 (2027-04-08): Callosotomy for drop attacks
- D190 (2027-04-09): Hypothalamic hamartoma gelastic epilepsy
- D191 (2027-04-10): Norman Dott and modern pain lesioning legacy
- D192 (2027-04-11): Closed-loop neuromodulation future
- D193 (2027-04-12): Tremor in MS surgical options
- D194 (2027-04-13): Facial pain differential before MVD
- D195 (2027-04-14): Neuromodulation clinic follow-up models

### Trauma (30)

- D136 (2027-02-14): Severe TBI: tiered ICP management
- D137 (2027-02-15): Decompressive craniectomy after RESCUEicp and DECRA
- D138 (2027-02-16): Mild TBI: return-to-play and return-to-work
- D139 (2027-02-17): TBI-associated coagulopathy
- D140 (2027-02-18): Pediatric TBI imaging decision rules
- D141 (2027-02-19): Penetrating brain injury modern care
- D142 (2027-02-20): Blast TBI and polytrauma priorities
- D143 (2027-02-21): Spinal cord injury ASIA grading
- D144 (2027-02-22): Early decompressive surgery in SCI
- D145 (2027-02-23): Methylprednisolone in SCI: current stance
- D146 (2027-02-24): Neurogenic shock vs hypovolemic shock
- D147 (2027-02-25): Cranioplasty timing after decompressive craniectomy
- D148 (2027-02-26): Post-traumatic hydrocephalus
- D149 (2027-02-27): Chronic traumatic encephalopathy counseling
- D150 (2027-02-28): TBI tracheostomy timing
- D151 (2027-03-01): Venous thromboembolism prophylaxis in TBI
- D152 (2027-03-02): Seizure prophylaxis after severe TBI
- D153 (2027-03-03): Hypothermia for TBI: trial takeaways
- D154 (2027-03-04): Multimodal neuromonitoring in TBI
- D155 (2027-03-05): Gunshot spine injury surgical roles
- D156 (2027-03-06): Atlanto-occipital dissociation
- D157 (2027-03-07): Growing skull fracture in children
- D158 (2027-03-08): TBI rehabilitation early mobilization
- D159 (2027-03-09): Disorders of consciousness prognosis
- D160 (2027-03-10): Second impact syndrome awareness
- D161 (2027-03-11): Trauma systems and neurosurgery coverage
- D162 (2027-03-12): Coagulopathic elderly ground-level falls
- D163 (2027-03-13): CSF leak after basilar skull fracture
- D164 (2027-03-14): Facial nerve injury in temporal bone trauma
- D165 (2027-03-15): SCI regenerative trials realistic outlook

### Pediatric (25)

- D196 (2027-04-15): Myelomeningocele prenatal vs postnatal repair
- D197 (2027-04-16): Chiari I decompression criteria in kids
- D198 (2027-04-17): Pediatric hydrocephalus ETV vs shunt
- D199 (2027-04-18): Shunt infection prevention in infants
- D200 (2027-04-19): Craniosynostosis endoscopic vs open
- D201 (2027-04-20): Sagittal synostosis scaphocephaly care
- D202 (2027-04-21): Syndromic craniosynostosis airway/ICP
- D203 (2027-04-22): Pediatric brain tumor posterior fossa approach
- D204 (2027-04-23): Infantile spasms neurosurgical intersections
- D205 (2027-04-24): Pediatric AVM hemorrhage risk
- D206 (2027-04-25): Abusive head trauma neurosurgical role
- D207 (2027-04-26): Neonatal IVH and posthemorrhagic hydrocephalus
- D208 (2027-04-27): Pediatric spine trauma clearance
- D209 (2027-04-28): Tethered cord release indications
- D210 (2027-04-29): Encephalocele repair principles
- D211 (2027-04-30): Pediatric pituitary / sellar lesions
- D212 (2027-05-01): Moyamoya in children surgical timing
- D213 (2027-05-02): Antenatal counseling for CNS anomalies
- D214 (2027-05-03): Vein of Galen malformation management
- D215 (2027-05-04): Pediatric chronic SDH / benign enlargement
- D216 (2027-05-05): School re-entry after brain tumor
- D217 (2027-05-06): Growing rod / MCGR complications neurosurgeons see
- D218 (2027-05-07): Congenital dermal sinus tract infection
- D219 (2027-05-08): Pediatric ICP monitoring thresholds
- D220 (2027-05-09): Transition of care to adult neurosurgery

### Critical care (20)

- D276 (2027-07-04): Neuro ICU blood pressure after ICH
- D277 (2027-07-05): Sodium management in SAH/TBI
- D278 (2027-07-06): Fever control in acute brain injury
- D279 (2027-07-07): Glycemic control in neuro ICU
- D280 (2027-07-08): Ventilation strategies protecting ICP
- D281 (2027-07-09): Sedation and delirium in the neurosurgical ICU
- D282 (2027-07-10): Brain death determination standards
- D283 (2027-07-11): Neuroprognostication after cardiac arrest
- D284 (2027-07-12): External ventricular drain leveling and drainage protocols
- D285 (2027-07-13): Continuous EEG in SAH and TBI
- D286 (2027-07-14): Transcranial Doppler in SAH
- D287 (2027-07-15): Nutrition in severe TBI
- D288 (2027-07-16): IVC filters in the neuro ICU: ongoing controversy
- D289 (2027-07-17): Post-craniotomy hypertensive crises
- D290 (2027-07-18): Neurogenic pulmonary edema
- D291 (2027-07-19): Status epilepticus ICU treatment algorithm
- D292 (2027-07-20): Osmotherapy: mannitol versus hypertonic saline
- D293 (2027-07-21): Automated pupillometry trending
- D294 (2027-07-22): Family communication in the neuro ICU
- D295 (2027-07-23): ICU liberation ABCDEF bundle in neuro patients

### Ethics / guidelines (20)

- D346 (2027-09-12): Informed consent for elective neurosurgery
- D347 (2027-09-13): Second opinion culture in brain tumors
- D348 (2027-09-14): Goals of care after devastating ICH/TBI
- D349 (2027-09-15): Surgical tourism risks in spine/neuromodulation
- D350 (2027-09-16): Conflicts of interest in device-heavy spine care
- D351 (2027-09-17): Pediatric assent alongside parental consent
- D352 (2027-09-18): Research consent for intraoperative tissue banking
- D353 (2027-09-19): Social media medical advice boundaries
- D354 (2027-09-20): Guideline literacy: AANS/CNS vs local adaptation
- D355 (2027-09-21): Antimicrobial stewardship in neurosurgery
- D356 (2027-09-22): Disclosure of intraoperative complications
- D357 (2027-09-23): Capacity assessment before high-risk surgery
- D358 (2027-09-24): Equity in EVT and aneurysm care access
- D359 (2027-09-25): Do-not-escalate orders in neuro ICU clarity
- D360 (2027-09-26): Trainee autonomy graded responsibility
- D361 (2027-09-27): Religious and cultural end-of-life sensitivities
- D362 (2027-09-28): Incidental germline findings in tumor NGS
- D363 (2027-09-29): Industry-sponsored trial enrollment counseling
- D364 (2027-09-30): Documentation standards for medicolegal resilience
- D365 (2027-10-01): One-topic daily public education ethics

### Hydrocephalus / CSF (20)

- D236 (2027-05-25): Normal pressure hydrocephalus triage
- D237 (2027-05-26): VP vs LP shunt selection
- D238 (2027-05-27): Programmable valve practical use
- D239 (2027-05-28): ETV for obstructive hydrocephalus adults
- D240 (2027-05-29): Shunt malfunction emergency pathway
- D241 (2027-05-30): IIH surgical options when meds fail
- D242 (2027-05-31): Spontaneous intracranial hypotension
- D243 (2027-06-01): Postoperative CSF leak cranial repair
- D244 (2027-06-02): Spinal CSF leak after lumbar puncture
- D245 (2027-06-03): Slit ventricle syndrome
- D246 (2027-06-04): Antibiotic-impregnated catheters evidence
- D247 (2027-06-05): Choroid plexus cauterization with ETV
- D248 (2027-06-06): Colloid cyst sudden death risk counseling
- D249 (2027-06-07): Hydrocephalus after SAH/TBI EVD wean
- D250 (2027-06-08): MRI safety and programmable valves
- D251 (2027-06-09): Abdominal complications of VP shunts
- D252 (2027-06-10): Low-pressure headache after shunt
- D253 (2027-06-11): CSF biomarkers in hydrocephalus research
- D254 (2027-06-12): Endoscopic septum pellucidotomy
- D255 (2027-06-13): Shunt independence campaigns caution

### Imaging / diagnostics (20)

- D296 (2027-07-24): Perfusion imaging for endovascular thrombectomy selection
- D297 (2027-07-25): Intracranial vessel-wall MRI: vasculitis versus atherosclerosis
- D298 (2027-07-26): Preoperative fMRI and DTI tractography planning
- D299 (2027-07-27): Amino-acid PET (e.g., FET) in glioma
- D300 (2027-07-28): Photon-counting CT: neuroradiologic applications
- D301 (2027-07-29): Ultra-high-field 7T MRI clinical niches
- D302 (2027-07-30): Spinal cord diffusion tensor imaging research
- D303 (2027-07-31): Contrast allergy protocols for neuro CT/MRI
- D304 (2027-08-01): Counseling incidental white-matter lesions
- D305 (2027-08-02): AI triage tools for ICH on noncontrast CT
- D306 (2027-08-03): Intraoperative ultrasound elastography
- D307 (2027-08-04): Dynamic CSF-flow MRI in Chiari and NPH
- D308 (2027-08-05): Dual-energy CT for bone/iodine separation
- D309 (2027-08-06): Quantitative pupillometry correlated with imaging
- D310 (2027-08-07): EOS/low-dose slot-scanning alignment imaging for spine
- D311 (2027-08-08): MR spectroscopy in brain lesion characterization
- D312 (2027-08-09): Black-blood MRI after flow diversion
- D313 (2027-08-10): Portable low-field MRI in the neuro ICU
- D314 (2027-08-11): Radiomics in meningioma and glioma research
- D315 (2027-08-12): Screening brain MRI in asymptomatic athletes: ethical angle

### Infection / inflammation (20)

- D256 (2027-06-14): Brain abscess modern drainage + antibiotics
- D257 (2027-06-15): Subdural empyema emergency
- D258 (2027-06-16): Post-craniotomy bone flap infection
- D259 (2027-06-17): Ventriculitis diagnosis and catheter strategies
- D260 (2027-06-18): Neurocysticercosis surgery indications
- D261 (2027-06-19): Tuberculoma vs tumor differentiation
- D262 (2027-06-20): Mucormycosis cranial invasion
- D263 (2027-06-21): Post-spine instrumentation infection biofilms
- D264 (2027-06-22): Viral encephalitis neurosurgical adjuncts
- D265 (2027-06-23): Autoimmune encephalitis antibody era
- D266 (2027-06-24): MOGAD and NMOSD neurosurgical pitfalls
- D267 (2027-06-25): COVID-related neurovascular sequelae literacy
- D268 (2027-06-26): Postoperative meningitis after skull base surgery
- D269 (2027-06-27): Intramedullary abscess rare entity
- D270 (2027-06-28): Hydatid disease of CNS
- D271 (2027-06-29): Prion disease red flags for the surgeon
- D272 (2027-06-30): Neuro-Behçet surgical emergencies
- D273 (2027-07-01): Sarcoid of the CNS mass lesions
- D274 (2027-07-02): Immune reconstitution inflammatory syndromes CNS
- D275 (2027-07-03): Antibiotic prophylaxis in clean craniotomy

### Neuro-oncology medical (15)

- D316 (2027-08-13): Temozolomide and MGMT in GBM care
- D317 (2027-08-14): Tumor treating fields real-world adherence
- D318 (2027-08-15): IDH inhibitors in glioma
- D319 (2027-08-16): BRAF/MEK targeted therapy in CNS tumors
- D320 (2027-08-17): Checkpoint inhibitors in brain mets / GBM limits
- D321 (2027-08-18): Bevacizumab for recurrent GBM / radiation necrosis
- D322 (2027-08-19): PCNSL methotrexate regimens and surgery limits
- D323 (2027-08-20): Medulloblastoma molecular therapy frontiers
- D324 (2027-08-21): Meningioma somatostatin receptor theranostics
- D325 (2027-08-22): Proton therapy for CNS tumors indications
- D326 (2027-08-23): CAR-T in CNS malignancy research status
- D327 (2027-08-24): Oncolytic virus therapy neurosurgical delivery
- D328 (2027-08-25): Seizure meds interacting with chemo/TKIs
- D329 (2027-08-26): Fertility preservation before cranial RT/chemo
- D330 (2027-08-27): Palliative care concurrent with neuro-oncology

### Peripheral nerve (15)

- D221 (2027-05-10): Carpal tunnel release indication refinement
- D222 (2027-05-11): Ulnar nerve decompression vs transposition
- D223 (2027-05-12): Brachial plexus birth injury timing
- D224 (2027-05-13): Adult traumatic brachial plexus repair
- D225 (2027-05-14): Peroneal nerve palsy foot drop
- D226 (2027-05-15): Meralgia paresthetica surgical options
- D227 (2027-05-16): Peripheral nerve sheath tumor resection
- D228 (2027-05-17): Nerve transfer for spinal cord injury
- D229 (2027-05-18): Iatrogenic nerve injury repair windows
- D230 (2027-05-19): Thoracic outlet neurosurgical role
- D231 (2027-05-20): Facial nerve reanimation after injury
- D232 (2027-05-21): Diabetic amyotrophy vs entrapment
- D233 (2027-05-22): Ultrasound-guided nerve hydrodissection
- D234 (2027-05-23): Gunshot nerve injury expectant vs early explore
- D235 (2027-05-24): Painful neuroma surgical strategies

### Rehabilitation / outcomes (15)

- D331 (2027-08-28): Early physiatry after stroke and TBI
- D332 (2027-08-29): Constraint-induced movement therapy
- D333 (2027-08-30): Cognitive rehab after aneurysmal SAH
- D334 (2027-08-31): Sphincter rehab after cauda equina
- D335 (2027-09-01): Robotic gait training after SCI
- D336 (2027-09-02): Vestibular rehab after vestibular schwannoma
- D337 (2027-09-03): Speech therapy after awake glioma surgery
- D338 (2027-09-04): PROMs in spine surgery
- D339 (2027-09-05): Return to driving after craniotomy/seizure
- D340 (2027-09-06): Caregiver burden after severe TBI
- D341 (2027-09-07): Vocational rehab after mild-moderate TBI
- D342 (2027-09-08): Spasticity management ladder postop/SCI
- D343 (2027-09-09): Neurogenic bladder permanent options
- D344 (2027-09-10): Quality of life after vestibular schwannoma pathways
- D345 (2027-09-11): Long-term surveillance fatigue in tumor survivors

---

*Dr. Wasif Rizwan Malik | The Neuro Council | drwasifmalik.com*
