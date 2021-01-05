counter=0
correct=0
for directory in $(find ~/FER/PPJ/ppj-compiler/lab3/lab3_teza/* -maxdepth 1 -type d)
do
	counter=$((counter+1))
	result="${directory%"${directory##*[!/]}"}"
	result="${result##*/}"
   # pokreni program i provjeri izlaz
	res=`python3 SemantickiAnalizator.py < $directory/$result.in | diff $directory/$result.out -`
	if [ "$res" != "" ]
	then
		echo "Test $result"
		# izlazi ne odgovaraju
		echo "FAIL"
		echo $res
	else
		correct=$((correct+1))
		fi
done
echo "scale=2 ; $correct / $counter * 100" | bc
echo $correct
