package main

import (
	"fmt"
	"os"
	"unsafe"
)

type beep [16]int

type boop [16]byte

type beepboop struct {
	beeps beep
	boops boop
}

var sheepshooopEnabled bool

func main() {
	sheepshooopEnabled = false

	fmt.Println("🤖 Beep Boop Converter 🤖")
	fmt.Println("-------------------------")
	fmt.Println("\nWhat do you want to do?")

	for {
		fmt.Println("1: BeepBoop Converter")
		fmt.Println("2: SheepShoop Converter")

		var choice int
		fmt.Print("> ")
		fmt.Scanf("%d", &choice)

		switch choice {
		case 1:
			convertBeepBoops()
		case 2:
			if sheepshooopEnabled {
				sheepshoop()
			} else {
				fmt.Println("SheepShoop is not enabled.")
			}
		default:
			fmt.Println("Bye!")
			return
		}
	}
}

func convertBeepBoops() {
	beeboo := beepboop{}

	fmt.Println("1: Convert Boops to Beeps")
	fmt.Println("2: Convert Beeps to Boops")

	var choice int
	fmt.Print("> ")
	fmt.Scanf("%d", &choice)

	if choice > 2 {
		fmt.Println("Unknown operation!")
		return
	}

	var amount int
	fmt.Print("How many: ")
	fmt.Scanf("%d", &amount)

	if choice == 1 {
		for i := 0; i < amount; i++ {
			var val byte
			fmt.Printf("%d> ", i)
			fmt.Scanf("%d", &val)

			beeboo.boops[i] = val
		}

		convert((*[128]byte)(unsafe.Pointer(&beeboo.beeps)), (*[128]byte)(unsafe.Pointer(&beeboo.boops)), amount)
	} else {
		for i := 0; i < amount; i++ {
			var val int
			fmt.Printf("%d> ", i)
			fmt.Scanf("%d", &val)

			beeboo.beeps[i] = val
		}
		convert((*[128]byte)(unsafe.Pointer(&beeboo.boops)), (*[128]byte)(unsafe.Pointer(&beeboo.beeps)), amount)
	}
}

func convert(dest, src *[128]byte, amount int) {
	for i := range amount * 8 {
		(*dest)[i] = (*src)[i]
	}
}

func sheepshoop() {
	flag := os.Getenv("FLAG")
	if flag == "" {
		fmt.Println("Flag is undefined, this is an error! Please contact us!")
	}

	fmt.Println(flag)
}
