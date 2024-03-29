PROG="python ../lts_learner_command.py --port $1"

$PROG --method GetNextWord
$PROG --method GetNextWorSd
$PROG l
$PROG --method SubmitPronunciation --word una --pronun "U N A"
$PROG --method SubmitPronunciation --word les --pronun "L E S"
$PROG --method SubmitPronunciation --word cep --pronun "TH E P"
$PROG --method SubmitPronunciation --word coy --pronun "K O I"
$PROG --method SubmitPronunciation --word cuy --pronun "K U I"
$PROG --method SubmitPronunciation --word yoc --pronun "Y O K"
$PROG --method SubmitPronunciation --word yic --pronun "Y I K"
$PROG --method SubmitPronunciation --word dyc --pronun "D Y K"

$PROG --method Get_LTS_Rules
$PROG --method PredictOneWord --word ley  --max_number 1 
$PROG --method PredictOneWord --word ley  --max_number 5 
$PROG --method PredictOneWord --word cey  --max_number 5 
$PROG --method PredictOneWord --word cey  --max_number 2 
$PROG --method PredictOneWord --word bim


$PROG --method SubmitPronunciation --word pib --pronun "P I B"
$PROG --method PredictOneWord --word lap 
$PROG --method GetRecentWordPronuns  
$PROG --method GetRecentWordPronuns  --max_number 5
$PROG --method Get_LTS_Rules
$PROG --method PercentFinished

for i in 1 2 3 4 5 6 7 8
do
  $PROG --method GetNextWord
done

$PROG --method PercentFinished
$PROG --method RemoveFromLexicon --word afp
$PROG --method WriteOutLexicon   --filename out/dictionary.lex
$PROG --method SynthesizeWord --word una
$PROG --method SynthesizeWord --word les

$PROG --method Shutdown

