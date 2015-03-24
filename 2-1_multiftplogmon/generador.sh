#!/bin/bash

NUM=0

while [ $NUM -lt 2 ];do
	n=$((RANDOM%500))
	dif=$((RANDOM%5))
	let m=$n+$dif

	sed -n $n,$m'p' logs_ftp/servidor1.log >> logs_ftp/servidor2.log
	sed -n $n,$m'p' logs_ftp/servidor2.log >> logs_ftp/servidor3.log
	sed -n $n,$m'p' logs_ftp/servidor3.log >> logs_ftp/servidor1.log
	
	let NUM=$NUM+1
done
