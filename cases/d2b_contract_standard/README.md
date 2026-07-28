# D2B domestic contract → Korean contract open standard

This Korean-to-Korean case uses only official schema metadata:

- Source: Defense Acquisition Program Administration, D2B domestic contract
  information (`getDmstcCntrctInfoList`).
- Target: Public Procurement Service contract data published according to the
  Korean public-data open standard (`getDataSetOpnStdCntrctInfo`).

The current gold mapping is a paper-trail draft, not independently reviewed
ground truth. `ornt` and `cntrctEntrpsNm` are explicitly marked as contextual
because the institutional roles may not be equivalent in every contract.

No API service key, contract row, company identifier, contact detail, or
operational defense record is stored here. No SCHEMORA run has been performed.
