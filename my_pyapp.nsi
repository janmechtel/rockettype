[% extends "pyapp.nsi" %]
LogSet On

; UI pages
[% block ui_pages %]
!define MUI_FINISHPAGE_RUN 
!define MUI_FINISHPAGE_RUN_TEXT "Start [[ib.appname]]"
!define MUI_FINISHPAGE_RUN_FUNCTION "LaunchLink"
[[ super() ]]
[% endblock ui_pages %]

;I don't know how we can get this function to be included into the generated installer.nsi
;For now i copied it into the pyapp.nsi inside the module  python38\lib\site-packages\nsist\pyapp.nsi
;Find out your path via pip show pynsist

;Function LaunchLink
;  ExecShell "" "$SMPROGRAMS\[[ib.appname]].lnk"
;FunctionEnd