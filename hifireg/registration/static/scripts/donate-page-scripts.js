        // // const charLimit = function(event) {
        // //   const { target } = event
        // //   const { value } = target
        // //   const decimalIndex = value.indexOf('.')
        // //   const inputCents = value.slice(decimalIndex)
        // //   if (inputCents.length > 3) {
        // //     const intCents = Math.floor(Number(value) * 100)
        // //     const strCents = String(intCents).padStart(3, '0')
        // //     const dollars = strCents.slice(0, -2)
        // //     const cents = strCents.slice(-2)
        // //     target.value = `${dollars}.${cents}`
        // //   }
        // // }
        // // const charFormat = function(event) {
        // //   event.target.value = Number(event.target.value).toFixed(2)
        // // }

        // const willThisWork = function(){
        //   debugger;
        //   console.log(`Value of element: ${document.getElementById('donationValue').value}`);
        // }

        //   const charLimit = function(event) {
        //   const { target, data } = event
        //   const { value } = target
        //   if(data === '.'){
        //     console.log(`Is event cancelable?: ${event.cancelable}`);
        //     alert("NOOOOOOOOOOOOOOOOOOOOOO");
        //     // console.log(`Value of element: ${document.getElementById('donationValue').value}`);
        //     document.getElementById('donationValue').value = value
        //   }
        //   if(value.includes('.')){
        //    const decimalIndex = value.indexOf('.')
        //    const valueWithoutDot = value.slice(0, decimalIndex)
        //    target.value = valueWithoutDot
        //   }
        //   // const inputCents = value.slice(decimalIndex)
        //   // if (inputCents.length > 3) {
        //   //   const intCents = Math.floor(Number(value) * 100)
        //   //   const strCents = String(intCents).padStart(3, '0')
        //   //   const dollars = strCents.slice(0, -2)
        //   //   const cents = strCents.slice(-2)
        //   //   target.value = `${dollars}.${cents}`
        //   // }
        // }