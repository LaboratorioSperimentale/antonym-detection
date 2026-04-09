# ANTONYM DETECTION

This repository contains code and data for an ongoing project that investigates antonymy detection through **constructional information encoded in contextual embeddings**.

The core idea is to move beyond purely lexical approaches to antonymy and explore whether **distributional and constructional patterns**, as captured by pretrained language models, can support the identification of antonymic relations.

---

## Data sources

### Italian data: CORIS (Corpus di Italiano Scritto contemporaneo)

The Italian dataset is extracted from the *Corpus di Italiano Scritto contemporaneo* (CORIS), a large-scale reference corpus of contemporary written Italian developed at the University of Bologna.

CORIS is designed to be representative of authentic written Italian across a range of genres, including:
- press  
- narrative  
- academic prose  
- administrative texts  

The corpus is annotated with part-of-speech tags and lemma information, making it suitable for corpus-based linguistic analysis. It also includes a **monitor component**, which is periodically updated to capture ongoing changes in language use.

---

### English data: COCA (Corpus of Contemporary American English)

The English dataset is extracted from the *Corpus of Contemporary American English* (COCA), a large and balanced corpus covering:
- spoken language  
- fiction  
- magazines  
- newspapers  
- academic texts  

---

## Data extraction

Data extraction is based on:
- a set of **seed antonym pairs** from Steven Jones (2002), *Antonymy: A Corpus-Based Perspective*  
- a set of **constructional patterns** in which antonymy is attested (e.g. *X and Y*, *from X to Y*, *either X or Y*)

### Potentially positive instances

Potentially positive instances are extracted by combining:
- a pattern  
- a seed pair *(X, Y)*  

These are contexts where antonymy is expected to occur.

### Potentially negative instances

Potentially negative instances are extracted by:
- combining a pattern with **only one member** of the seed pair *(X or Y)*  
- retrieving a different adjective (same POS) in the other slot  

This procedure generates structurally similar contexts that are **not guaranteed to express antonymy**, allowing for controlled contrast.

---

## Annotation

Manual annotation is a crucial step in the pipeline.

Some automatically extracted *negative candidates* may still express antonymy, for example when:
- the retrieved adjective is a **synonym or near-antonym** of the seed pair element  
- the construction still conveys a contrastive meaning  

Conversely, many extracted pairs do not form valid antonymic relations and represent true negative instances.

Each occurrence is manually annotated to determine its actual semantic status.

---

## Dataset structure

Each occurrence is associated with a **unique ID**:
- for English data: IDs are generated automatically  
- for Italian data: IDs correspond to the original CORIS sentence (ensuring uniqueness, with at most one instance per sentence)

### Fields

- **id**: unique identifier  
- **class**: `"yes"` / `"no"` (candidate label from extraction)  
- **pattern**: constructional pattern (e.g. *X and Y*, *from X to Y*)  
- **X_found**: surface form of the first adjective  
- **Y_found**: surface form of the second adjective  
- **pair**: lemmatized original seed pair (e.g. *big–small*)  
- **context_pre**: left context  
- **costr**: construction span  
- **context_post**: right context  

### Annotation labels

- **ANTONYMOUS**  
  The instance expresses a genuine antonymic relation.

- **NOT_ANTONYMOUS**  
  The instance does not express antonymy.

- **IDIOSYNCRATIC**  
  The construction is formally matched but does not convey a compositional antonymic meaning (e.g. fixed expressions or context-specific uses).  
  Example:  
  *"Dopo gli alti e bassi degli anni passati, in questo periodo le quotazioni sono scese."*

- **ERROR**  
  The instance is invalid due to noise or extraction errors. This includes:
  - corrupted or noisy sentences  
    Example:  
    *"At @ @ @ @ @ @ @ @ @ @ alive or dead."*  
  - cases where the matched sequence does not correspond to an actual construction  
    Example:  
    *"Già allora il regista manifestava una predilezione per i caratteri femminili..."*

---

## Notes

- The project is ongoing, and both data and code are subject to updates.