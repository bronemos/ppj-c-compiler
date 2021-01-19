counter=0
correct=0
for directory in $(find ~/FER/PPJ/ppj-compiler/lab4/1-t/* -maxdepth 1 -type d)
do
	counter=$((counter+1))
	result="${directory%"${directory##*[!/]}"}"
	result="${result##*/}"
   # pokreni program i provjeri izlaz
	res1=`python3 GeneratorKoda.py < $directory/test.in`
	res=`node main.js a.frisc 2> err.txt| diff $directory/test.out -`
	if [ "$res" != "" ]
	then
		echo "Test $result"
		# izlazi ne odgovaraju
		echo "FAIL"
		echo $res
	else
	echo "Test $result"
		echo "OK"
		correct=$((correct+1))
		fi
done
echo "scale=2 ; $correct / $counter * 100" | bc
echo $correct
