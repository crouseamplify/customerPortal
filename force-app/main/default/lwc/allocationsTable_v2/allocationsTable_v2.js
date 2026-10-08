import { LightningElement, track, api } from 'lwc';
import ConfigureModal from 'c/configureModal';
import CreateOAModal from 'c/createOAModal';

export default class AllocationsTable extends LightningElement {
    constructor() {
        super();
        this.boundHandleMouseEnter = this.handleMouseEnter.bind(this);
        this.boundHandleMouseLeave = this.handleMouseLeave.bind(this);
    }
	// --- API Properties ---
	@api orderAllocations;
	@api bsoProducts;
	@api orderAllocationProducts;
	@api blanketSaleOrder;
	@api orderAllocationRequest;
	@api tableOutput = [];
	@api allocationProductsOutput = [];
	@api Coll_Order_Allocation_Products;
	@api orderAllocationProductsOutput = [];
	@api bsoProductsOutput = [];
    @api usePagination;
    @api hideNewAllocationButton;
    @api deletedAllocations = [];
   

	// --- Tracked Properties ---
	@track bsoProductsArray;
	@track orderAllocationsArray;
	@track orderAllocationProductsArray;
	@track paginationState = {
		totalItems: 0,
		itemsPerPage: 20,
		currentPage: 1,
		totalPages: 1,
		showingRecordsStart: 0,
		showingRecordsEnd: 0,
		disableNextPage: true,
		disablePreviousPage: true,
		disableAllPagination: true
	};
    @track searchSuggestions = [];
    @track showSuggestions = false;
    @track cellValueCache = new Map();


	// --- Private Properties ---
	productSearchValue = "";
	availableCalc = false;
	disabled = false;
	hasRendered = false;
	inputCells = [];
	remainingCells = [];
	isNotFinalYear = true;
	editMode = true;
	searchDebounceTimer;
	currentPageProducts = [];
	isLoading = false;
	usingProductsArray = [];
    debouncedUpdate = null;
    lastUpdatedCell = null;

	// --- Lifecycle Hooks ---
	connectedCallback() {
        console.log(this.usePagination);
		if(this.blanketSaleOrder.Multi_Year__c === true && 
		   this.blanketSaleOrder.Is_this_the_final_year__c === false) {
			this.isNotFinalYear = !this.orderAllocations[0].Lock_Allocation__c;
		} else {
			this.isNotFinalYear = false;
		}

		if (this.orderAllocationRequest.Status__c != "Open") {
			this.hideNewAllocationButton = true;
		}

		// Initialize arrays
		this.initializeArrays();
		
		// Set initial pagination
		this.usingProductsArray = this.bsoProductsArray;
		this.calcTotalProducts();

        //Create a unique list of BSO product Programs for filtering
        this.familyOptions = Array.from([...new Set(this.bsoProductsArray.map(product => product.Program__c))], (program) => new Object({label: program, value: program}));
        this.familyOptions.unshift({label: 'None', value: ''});

		// Set configuration status for allocations
		this.orderAllocationsArray.forEach(allocation => {
			this.setConfigureStatus(allocation);
		});

        // Add initial caching
         if (this.orderAllocationProducts) {
            this.orderAllocationProducts.forEach(oaProduct => {
                const cacheKey = `${oaProduct.Blanket_Sales_Order_Product__c}-${oaProduct.Order_Allocation__c}`;
                this.cellValueCache.set(cacheKey, oaProduct.Quantity__c || 0);
            });
    }
}

	renderedCallback() {
		if (!this.hasRendered) {
			this.isLoading = false;
			this.initializeCells();
			this.updateTableCalculations();
			this.availableCalc = true;
			this.hasRendered = true;
		}
		this.updateRemainingCellsDisplay();
	}

	// --- Pagination Methods ---
	calculatePaginationState(totalItems, itemsPerPage, currentPage) {
		const validatedState = {
			totalItems: Math.max(0, totalItems || 0),
			itemsPerPage: Math.max(1, itemsPerPage || 20),
			currentPage: Math.max(1, currentPage || 1)
		};

		const totalPages = Math.max(1, Math.ceil(validatedState.totalItems / validatedState.itemsPerPage));
		const validCurrentPage = Math.min(Math.max(1, validatedState.currentPage), totalPages);
		const startIndex = (validCurrentPage - 1) * validatedState.itemsPerPage;
		const endIndex = Math.min(startIndex + validatedState.itemsPerPage, validatedState.totalItems);

		return {
			totalPages,
			currentPage: validCurrentPage,
			startIndex,
			endIndex,
			showingRecordsStart: startIndex + 1,
			showingRecordsEnd: endIndex,
			disableNextPage: validCurrentPage >= totalPages,
			disablePreviousPage: validCurrentPage <= 1,
			disableAllPagination: totalPages <= 1
		};
	}

	calcPages() {
        const newState = this.calculatePaginationState(
            this.totalNumberOfProducts,
            this.paginationState.itemsPerPage === 'all' ? this.totalNumberOfProducts : this.paginationState.itemsPerPage,
            this.paginationState.currentPage
        );
    
        this.paginationState = { 
            ...this.paginationState, 
            ...newState,
            showingRecordsStart: newState.startIndex + 1,  // Fix for showing record numbers
            showingRecordsEnd: newState.endIndex,
            currentPage: newState.currentPage,
            totalPages: newState.totalPages
        };
    
        // Update navigation button states
        this.paginationState.disablePreviousPage = this.paginationState.currentPage <= 1;
        this.paginationState.disableNextPage = this.paginationState.currentPage >= this.paginationState.totalPages;
    
        this.calcProductsToDisplay();
    }

	calcTotalProducts() {
		this.totalNumberOfProducts = this.usingProductsArray.length;
		this.calcPages();
	}

	calcProductsToDisplay() {
		const start = (this.paginationState.currentPage - 1) * this.paginationState.itemsPerPage;
		const end = start + this.paginationState.itemsPerPage;
        if(!this.usePagination) {
            this.currentPageProducts = this.usingProductsArray;

            //Need logic to reset the firstOFFamily checkbox everytime the table is refreshed (search is used)
            /*let previousFamily = null;

            for (let i = 0; i < this.currentPageProducts.length; i++) {
                const record = this.currentPageProducts[i];
                record.firstOfFamily = record.Product_Family__c !== previousFamily;
                record.color = "red"
                previousFamily = record.Product_Family__c;
            }

            console.table(this.currentPageProducts);*/
        } else {
            this.currentPageProducts = this.usingProductsArray.slice(start, end);

            /*let previousFamily = null;

            for (let i = 0; i < this.currentPageProducts.length; i++) {
                const record = this.currentPageProducts[i];
                record.firstOfFamily = record.Product_Family__c !== previousFamily;
                previousFamily = record.Product_Family__c;
            }

            console.table(this.currentPageProducts);*/
        }
	}



	// --- Navigation Methods ---
    handlePageNavigation(newPage) {
        this.cacheCellValues();
        this.isLoading = true;
        setTimeout(() => {
            this.hasRendered = false;
            this.availableCalc = false;
            this.paginationState.currentPage = newPage;
            this.calcPages();
            this.isLoading = false;
        }, 1);
    }
    
    handleFirst() {
        if (!this.paginationState.disablePreviousPage) {
            this.handlePageNavigation(1);
        }
    }
    
    handleLast() {
        if (!this.paginationState.disableNextPage) {
            this.handlePageNavigation(this.paginationState.totalPages);
        }
    }
    
    pageIncrement() {
        if (!this.paginationState.disableNextPage) {
            this.handlePageNavigation(this.paginationState.currentPage + 1);
        }
    }
    
    pageDecrement() {
        if (!this.paginationState.disablePreviousPage) {
            this.handlePageNavigation(this.paginationState.currentPage - 1);
        }
    }
    
    navigateToPage(event) {
        let pageNum = Math.max(1, parseInt(event.detail.value, 10));
        pageNum = Math.min(pageNum, this.paginationState.totalPages);
        
        const input = this.template.querySelector('lightning-input[data-id="pageInput"]');
        if (input) {
            input.value = pageNum.toString();
        }
        
        this.handlePageNavigation(pageNum);
    }

    changeItemsPerPage(event) {
        this.isLoading = true;
        setTimeout(() => {
            this.hasRendered = false;
            
            // Cache values before changing page size
            this.cacheCellValues();
    
            const newValue = event.detail.value;
            this.paginationState.itemsPerPage = newValue === 'all' ? 
                this.totalNumberOfProducts : 
                parseInt(newValue, 10);
    
            this.paginationState.currentPage = 1;
            this.calcPages();
            this.isLoading = false;
        }, 1);
    }

    //
    familyValue = '';

    /*get familyOptions() {
        return [
            { label: 'None', value: ''},
            { label: 'Amplify ELA', value: 'Amplify ELA'},
            { label: 'Amplify Science', value: 'Amplify Science'},
            { label: 'Amplify Math', value: 'Amplify Math'},
            { label: 'Burst', value: 'Burst'},
            { label: 'CKLA', value: 'CKLA'},
            { label: 'mCLASS', value: 'mCLASS'},
            { label: 'PLM', value: 'PLM'},
            { label: 'Seeds of Science', value: 'Seeds of Science'},
            { label: 'Shipping and Handling', value: 'Shipping and Handling'},
            { label: 'Supplementals', value: 'Supplementals'},
            { label: 'Coaching', value: 'Coaching'},
            { label: 'Amplify Tutoring', value: 'Amplify Tutoring'},
            { label: 'Multi Product', value: 'Multi Product'},
            { label: 'Mathigon', value: 'Mathigon'},
            { label: 'Desmos Math', value: 'Desmos Math'},
        ];
    }*/

    familyPicklist(event) {
        this.familyValue = event.detail.value;
        this.hasRendered = false;
        if(this.searchTerm) {
            const searchedProducts = this.searchHandler(this.searchTerm);
            this.usingProductsArray = this.filterFamilyProducts(searchedProducts, this.familyValue);
        } else {
            this.usingProductsArray = this.filterFamilyProducts(this.bsoProductsArray, this.familyValue);
        }
        this.resetAndUpdateTable();
    }

    filterFamilyProducts(products, family) {
        if (!family) {
            return products; // return all if family is empty string, null, or undefined
        }
            return products.filter(p => p.Program__c === family);
    }

    handleUnfocus() {
        //can't click suggestions anymore
        setTimeout(() => {
            this.showSuggestions = false;
        }, 500);
    }

    searchTerm = null;

    //
	// --- Search Methods ---
    handleSearch(event) {
        this.searchTerm = event.target.value;
        this.searchHandler(this.searchTerm);
    }

    searchHandler(searchValue) {
        this.searchTerm = searchValue;
        console.log('Before search cache:', new Map(this.cellValueCache));
        
        clearTimeout(this.searchDebounceTimer);
        this.productSearchValue = searchValue;
        let searchTerm = this.productSearchValue.trim().toLowerCase();
        
        this.cacheCellValues();
        console.log('After cache:', new Map(this.cellValueCache));
        
        if (!searchTerm) {
            this.resetSearch();
            return;
        }
    
        this.searchSuggestions = this.filterProducts(searchTerm, true);
        const searchEle = this.template.querySelector('[data-search-box]');
        const focusedEle = this.template.activeElement;
        this.showSuggestions = (this.searchSuggestions.length > 0) && (searchEle === focusedEle);
    
        this.searchDebounceTimer = setTimeout(() => {
            console.log('Before update:', new Map(this.cellValueCache));
            this.hasRendered = false;
            this.usingProductsArray = this.filterProducts(searchTerm);
            this.usingProductsArray = this.filterFamilyProducts(this.usingProductsArray, this.familyValue);
            this.resetAndUpdateTable();
        }, 350);
    }

    handleSuggestionSelect(event) {
        this.searchHandler(event.target.dataset.name);
    }
    
    
    filterProducts(searchTerm, getSuggestions = false) {
        const filtered = this.bsoProductsArray.filter(product => {
            const nameMatch = product.Product_Name__c.toLowerCase().includes(searchTerm);
            const isbnMatch = product.Product_ISBN__c?.toLowerCase().includes(searchTerm);
            return nameMatch || isbnMatch;
        });
    
        return getSuggestions ? 
            filtered.slice(0, 3).map(product => ({
                id: product.Id,
                display: `${product.Product_Name__c} (${product.Product_ISBN__c || ''})`,
                name: `${product.Product_Name__c}`
            })) : 
            filtered;
    }
    
    resetSearch() {
        this.hasRendered = false;
        this.searchTerm = null;
        //this.availableCalc = false;
        this.searchSuggestions = [];
        this.showSuggestions = false;
        this.usingProductsArray = this.bsoProductsArray;
        this.usingProductsArray = this.filterFamilyProducts(this.usingProductsArray, this.familyValue);
        this.calcTotalProducts();
    }
    
    resetAndUpdateTable() {
        this.hasRendered = false;
        //this.availableCalc = false;
        this.paginationState.currentPage = 1;
        this.calcTotalProducts();
        
        // Update cell values from cache before calculations
        this.inputCells.forEach(inputCell => {
            const productId = inputCell.dataset.productId;
            const allocationId = inputCell.dataset.allocationId;
            const cacheKey = `${productId}-${allocationId}`;
            if (this.cellValueCache.has(cacheKey)) {
                inputCell.value = this.cellValueCache.get(cacheKey);
            }
        });
        
        //this.updateTableCalculations();
    }
    
    // --- Table Update Methods --- 
    updateTableRow(productId) {
        const bsoProduct = this.bsoProductsArray.find(p => p.Id === productId);
        if (!bsoProduct) return;
    
        const rowTotal = this.calculateRowTotal(productId);
    
    // Update order allocation products for this row
    this.updateOrderAllocationProducts(productId);

    // Update product values
    bsoProduct.Distributed = rowTotal;
    if (!this.availableCalc) {
        bsoProduct.Available = bsoProduct.Available_Quantity_Calculated__c + rowTotal;
    }
    bsoProduct.Remaining = bsoProduct.Available2 - bsoProduct.Distributed;

    // Update validation and outputs
    const cellsInThisRow = this.inputCells.filter(
        inputCell => inputCell.dataset.productId === productId
    );
    this.updateCellValidation(cellsInThisRow, bsoProduct);
    this.updateOutputArrays();
}

updateSingleRow(productId) {
    const bsoProduct = this.bsoProductsArray.find(p => p.Id === productId);
    if (!bsoProduct) return;
    console.log("cachekey");
    const rowTotal = this.calculateRowTotal(productId);
    this.updateOrderAllocationProducts(productId);
    bsoProduct.Distributed = rowTotal;
    if (!this.availableCalc) {
        bsoProduct.Available = bsoProduct.Available_Quantity_Calculated__c + rowTotal;
    }
    bsoProduct.Remaining = bsoProduct.Available2 - bsoProduct.Distributed;
    const cellsInThisRow = this.inputCells.filter(
        inputCell => inputCell.dataset.productId === productId
    );
    this.updateCellValidation(cellsInThisRow, bsoProduct);
    this.updateOutputArrays();
}

calculateRowTotal(productId) {
    const cellsInThisRow = this.inputCells.filter(
        inputCell => inputCell.dataset.productId === productId
    );
    return cellsInThisRow.reduce(
        (sum, cell) => sum + (parseFloat(cell.value) || 0),
        0
    );
}

calculateRowTotals(productId) {
    const cellsInThisRow = this.orderAllocationProductsArray.filter(
        inputCell => inputCell.Blanket_Sales_Order_Product__c === productId
    );
    let rowTotal = 0;
    cellsInThisRow.forEach(cell => { //loops through each cell in this row
        console.log(cell.Quantity__c);
        rowTotal += parseFloat(cell.Quantity__c) || 0; //adds the cell value to the row total
    });
    return rowTotal;
}

updateTableCells() {
    if (this.lastUpdatedCell) {
        const productId = this.lastUpdatedCell.dataset.productId;
        this.updateSingleRow(productId);
    }
    this.lastUpdatedCell = null;
}

performUpdate() {
    if (this.lastUpdatedCell) {
        const productId = this.lastUpdatedCell.dataset.productId;
        console.log("productId " + productId);
        this.updateSingleRow(productId);
    }
    this.bsoProductsOutput = this.bsoProductsArray.map(product => ({ Id: product.Id, Remaining_Quantity__c: product.Remaining }));
    this.orderAllocationProductsOutput = this.orderAllocationProductsArray;
    this.lastUpdatedCell = null;
}


updateOrderAllocationProducts(productId) {
    const cellsInThisRow = this.inputCells.filter(
        inputCell => inputCell.dataset.productId === productId
    );
    
    cellsInThisRow.forEach(inputCell => {
        const allocationId = inputCell.dataset.allocationId;
        const orderAllocationProduct = this.orderAllocationProductsArray.find(
            oAProduct => oAProduct.Blanket_Sales_Order_Product__c === productId && 
                        oAProduct.Order_Allocation__c === allocationId
        );
        if (orderAllocationProduct) {
            orderAllocationProduct.Quantity__c = parseFloat(inputCell.value) || 0;
        }
    });
}

	updateCellValidation(cells, product) {
		const isZeroRemaining = product.Remaining === 0;
		const isNegativeRemaining = product.Remaining < 0;

		cells.forEach(cell => {
			cell.classList.remove("error");
			cell.title = "";

			if (isZeroRemaining) {
				cell.max = parseFloat(cell.value) || 0;
			} else if (isNegativeRemaining) {
				cell.classList.add("error");
				cell.title = "Value exceeds qty. available";
				cell.max = 0;
			} else {
				cell.max = product.Available;
			}
		});
	}

	updateOutputArrays() {
		this.bsoProductsOutput = this.bsoProductsArray.map(product => ({ 
			Id: product.Id, 
			Remaining_Quantity__c: product.Remaining 
		}));
		this.orderAllocationProductsOutput = this.orderAllocationProductsArray;
	}

	// --- Cell Event Handlers ---
	handleDecrement(event) {
		this.handleQuantityChange(event, -1);
	}

	handleIncrement(event) {
		this.handleQuantityChange(event, 1);
	}

    handleQuantityChange(event, change) {
        const { allocationId, productId } = event.target.dataset;
        const inputCell = this.inputCells.find(cell => 
            cell.dataset.allocationId === allocationId && 
            cell.dataset.productId === productId
        );
    
        if (inputCell) {
            const newValue = Number(inputCell.value) + change;
            if (newValue >= 0 && (change < 0 || newValue <= inputCell.max)) {
                inputCell.value = newValue;
                this.lastUpdatedCell = inputCell;
                const key = `${event.target.dataset.productId}-${event.target.dataset.allocationId}`;
                this.cellValueCache.set(key, parseFloat(event.target.value) || 0); // Update cache
                this.performUpdate();
            }
        }
    }

	// --- Modal Handlers ---
	handleConfigureDetails(event) {
		const allocationId = event.target.dataset.id;
		ConfigureModal.open({
			allocationId: allocationId,
            size: 'small'
		}).then((result) => {
			if (result) {
				const orderAllocation = this.orderAllocationsArray.find(
					oA => oA.Id === allocationId
				);
				
				Object.keys(result[2]).forEach(field => {
					if (field !== "Id") {
						orderAllocation[field] = result[2][field];
					}
				});

				this.setConfigureStatus(orderAllocation);
			}
		});
	}

	handleCreateOrderAllocation(event) {
		CreateOAModal.open({
			bsoId: this.blanketSaleOrder.Id,
			oaRequestId: this.orderAllocationRequest.Id,
		}).then((result) => {
			if (result) {
				this.hasRendered = false;
				const [newAllocation, newProducts] = result;
				
				this.orderAllocationsArray = [...this.orderAllocationsArray, newAllocation];
				this.orderAllocationProductsArray = [...this.orderAllocationProductsArray, ...newProducts];
				
				this.setConfigureStatus(newAllocation);
			}
		});
	}

	/*handleRefreshAllocation(event) {
		const allocationId = event.target.dataset.id;
		
		// Reset quantities in data
		this.orderAllocationProductsArray.forEach(oaProduct => {
			if(oaProduct.Order_Allocation__c === allocationId) {
				oaProduct.Quantity__c = 0;
			}
		});
	
		// Reset input cells
		this.inputCells.forEach(inputCell => {
			if(inputCell.dataset.allocationId === allocationId) {
				inputCell.value = 0;
				inputCell.initialValue = 0;
			}
		});
	
		// Update calculations
		this.hasRendered = false;
		this.updateTableCells();
	}*/

    handleRefreshAllocation(event) {
        const allocationId = event.target.dataset.id;
        let oaProds = this.orderAllocationsArray.filter(product => 
            product.Id === allocationId
        );
    
        if (oaProds) {
            console.log('const2' + oaProds);
            oaProds.forEach(oaProd => {
                this.bsoProductsArray.forEach(bsoProd => {
                    const orderAllocationProduct = this.orderAllocationProductsArray.find(
                        oAProduct => oAProduct.Blanket_Sales_Order_Product__c === bsoProd.Id && 
                                    oAProduct.Order_Allocation__c === oaProd.Id
                    );
                    if (orderAllocationProduct) {
                        orderAllocationProduct.Quantity__c = 0;
                    }
                    const newValue = 0;
                    //if (newValue >= 0 && (change < 0 || newValue <= inputCell.max)) {
                    //cell.value = newValue;
                    //inputCell.value = newValue;
                    let inputCell = this.inputCells.find(input => 
                        input.dataset.allocationId === oaProd.Id && input.dataset.productId === bsoProd.Id
                    );
                    if(inputCell) {
                        inputCell.value = 0;
                        this.lastUpdatedCell = inputCell;
                    } else {
                        this.lastUpdatedCell = {dataset: {productId: bsoProd.Id, allocationId: oaProd.Id}}
                    }
                    oaProd.Quantity__c = 0;
                    //console.log('bsoPRod' + bsoProd.Id);
                    //console.log('oaProd' + oaProd.Id);
                    const key = `${bsoProd.Id}-${oaProd.Id}`;
                    this.cellValueCache.set(key, 0); // Update cache
                    this.performUpdate();

                });
            });
        }
    }

    // --- Handle Cancel Allocation ---
    handleCancelAllocation(event) {
        const allocationId = event.target.dataset.id;
        
        // Store the allocation ID for later status update
        if (!this.deletedAllocations.some(record => record.Id === allocationId)) {
            this.deletedAllocations.push({ Id: allocationId, Status__c: "Cancelled" });
            console.log("added");
        }
        
        // Hide the column
        const allocColumn = event.target.closest('th');
        if (allocColumn) {
            allocColumn.style.display = 'none';
            const columnIndex = Array.from(allocColumn.parentElement.children).indexOf(allocColumn);
            const table = this.template.querySelector('table');
            table.querySelectorAll('tr').forEach(row => {
                const cell = row.cells[columnIndex];
                if (cell) cell.style.display = 'none';
            });
        }
    
        // Reset quantities to 0
        this.handleRefreshAllocation(event);
    }

	// --- Helper Methods ---
    
	initializeArrays() {
        this.orderAllocationsArray = JSON.parse(JSON.stringify(this.orderAllocations));
        this.orderAllocationProductsArray = JSON.parse(JSON.stringify(this.orderAllocationProducts));
		// Initialize BSO Products
		this.bsoProductsArray = JSON.parse(JSON.stringify(this.bsoProducts));
		this.bsoProductsArray.forEach(product => {
            console.log(product);
			if (product.Product_ID__c == null) {
			product.Product_Name__c = product.Name;
			product.Product_ISBN__c = product.ISBN__c;
            //console.log("product: " + product.Product_ID__c + ", " + product.Product_Name__c + ", " + product.Available);
			}
            product.Available2 = product.Available_Quantity_Calculated__c + this.calculateRowTotals(product.Id);
		});

		// Initialize Order Allocations
		//this.orderAllocationsArray = JSON.parse(JSON.stringify(this.orderAllocations));
		
		// Initialize Order Allocation Products
	}

    initializeCells() {
        this.remainingCells = this.template.querySelectorAll('[data-id="remainingCell"]');
        this.remainingCells.forEach(cell => {
            if(parseInt(cell.outerText) < 0) {
                cell.classList.add("error");
            }
            cell.addEventListener('mouseenter', this.boundHandleMouseEnter);
            cell.addEventListener('mouseleave', this.boundHandleMouseLeave);
        });

        const inputCellList = this.template.querySelectorAll('[data-id="input"]');
        this.inputCells = [...inputCellList];
        this.initializeInputCellValues();
    }

    disconnectedCallback() {
        if (this.searchDebounceTimer) {
            clearTimeout(this.searchDebounceTimer);
        }
        if (this.debouncedUpdate) {
            clearTimeout(this.debouncedUpdate); 
        }
        
        this.remainingCells.forEach(cell => {
            cell.removeEventListener('mouseenter', this.boundHandleMouseEnter);
            cell.removeEventListener('mouseleave', this.boundHandleMouseLeave);
        });
    }

    initializeInputCellValues() {
        console.log('Cache during init:', new Map(this.cellValueCache));
        this.inputCells.forEach(inputCell => {
            const productId = inputCell.dataset.productId;
            const allocationId = inputCell.dataset.allocationId;
            const cacheKey = `${productId}-${allocationId}`;
            
            let value = 0;
            if (this.cellValueCache.has(cacheKey)) {
                value = this.cellValueCache.get(cacheKey);
            } else {
                const orderAllocationProduct = this.orderAllocationProductsArray.find(
                    oAProduct => oAProduct.Blanket_Sales_Order_Product__c === productId && 
                                oAProduct.Order_Allocation__c === allocationId
                );
                value = orderAllocationProduct ? 
                    (parseFloat(orderAllocationProduct.Quantity__c) || 0) : 
                    0;
                this.cellValueCache.set(cacheKey, value);
            }
            inputCell.value = value;
            inputCell.initialValue = value;
        });
    }

    cacheCellValues() {
        this.inputCells.forEach(cell => {
            const key = `${cell.dataset.productId}-${cell.dataset.allocationId}`;
            this.cellValueCache.set(key, parseFloat(cell.value) || 0);
        });
    }

    updateTableCalculations() {
        this.bsoProductsArray.forEach(bsoProduct => {
            const cellsInThisRow = this.inputCells.filter(
                inputCell => inputCell.dataset.productId === bsoProduct.Id
            );
    
            const rowTotal = cellsInThisRow.reduce(
                (total, cell) => total + (parseFloat(cell.value) || 0), 
                0
            );
            
            if(!this.availableCalc) {
                bsoProduct.Available = bsoProduct.Available_Quantity_Calculated__c + rowTotal;
            }
            bsoProduct.Distributed = rowTotal;
            bsoProduct.Remaining = bsoProduct.Available2 - bsoProduct.Distributed;
            
            this.updateCellValidation(cellsInThisRow, bsoProduct);
        });
    }
    
    updateCellValidation(cellsInThisRow, bsoProduct) {
        if (bsoProduct.Remaining === 0) {
            cellsInThisRow.forEach(cell => {
                cell.classList.remove("error");
                cell.title = "";
                cell.max = parseFloat(cell.value) || 0;
            });
        }
        else if (bsoProduct.Remaining < 0) {
            cellsInThisRow.forEach(cell => {
                cell.classList.add("error");
                cell.title = "Value exceeds qty. available";
                cell.max = 0;
            });
        }
        else {
            cellsInThisRow.forEach(cell => {
                cell.classList.remove("error");
                cell.title = "";
                cell.max = bsoProduct.Available;
            });
        }
    }
			
    updateRemainingCellsDisplay() {
        this.remainingCells.forEach(cell => {
            const remainingValue = parseInt(cell.outerText);
            const isZeroRemaining = remainingValue === 0;
            const isNegativeRemaining = remainingValue < 0;

            cell.classList.remove("warningRemaining", "errorRemaining");

            if (this.isNotFinalYear && isZeroRemaining) {
                cell.classList.add("warningRemaining");
            }
            if (isNegativeRemaining) {
                cell.classList.add("errorRemaining");
            }
        });
    }

    handleMouseEnter(event) {
        const remainingValue = parseInt(event.target.outerText);
        if(remainingValue < 0) {
            event.target.children[0].style.display = "inline";
        }
        if(event.target.classList.contains('warningRemaining')) {
            event.target.children[1].style.display = "inline";
        }
    }
    //Code changed to fix error with mouseLeave events on the record page.
    // handleMouseLeave(event) {
    //     event.target.children[0].style.display = "none";
    //     event.target.children[1].style.display = "none";
    // }

    handleMouseLeave(event) {
        const popoverElements = event.target.children;
        if (popoverElements[0]) popoverElements[0].style.display = "none";
        if (popoverElements[1]) popoverElements[1].style.display = "none";
    }

    setConfigureStatus(allocation) {
        if (!allocation.Status__c || allocation.Status__c === "New") {
            allocation.showConfigure = true;
            allocation.confirmed = false;
            allocation.submitted = false;
            allocation.inProgress = false;
        }
        else if (allocation.Status__c !== "Confirmed" && 
                    allocation.Status__c !== "Submitted" && 
                    allocation.Status__c !== "In Progress") {
            allocation.showConfigure = true;
            allocation.confirmed = false;
            allocation.submitted = false;
            allocation.inProgress = false;
        }
        else if (allocation.Status__c === "In Progress") {
            allocation.showConfigure = false;
            allocation.confirmed = false;
            allocation.submitted = false;
            allocation.inProgress = true;
        }
        else if (allocation.Status__c === "Confirmed" || allocation.Confirmed_Date__c) {
            allocation.showConfigure = false;
            allocation.confirmed = true;
            allocation.submitted = false;
            allocation.inProgress = false;
        }
    }

    get pageList() {
        return Array.from(
            { length: this.paginationState.totalPages },
            (_, i) => ({
                label: (i + 1).toString(),
                value: (i + 1).toString()
            })
        );
    }

    get currentPageString() {
        return this.paginationState.currentPage.toString();
    }

    get itemsPerPageString() {
        if (this.paginationState.itemsPerPage === this.totalNumberOfProducts) {
            return 'all';
        }
        return this.paginationState.itemsPerPage.toString();
    }

    itemsPerPageOptions = [
        {label: '5', value: '5'},
        {label: '10', value: '10'},
        {label: '15', value: '15'},
        {label: '20', value: '20'},
        {label: '25', value: '25'},
        {label: '30', value: '30'},
        {label: 'All', value: 'all'}
    ];

    handleToggle(event) {
        this.editMode = event.target.checked;
        this.hasRendered = false;
    }

    handleInput(event) {
        this.lastUpdatedCell = event.target;
        const key = `${event.target.dataset.productId}-${event.target.dataset.allocationId}`;
        this.cellValueCache.set(key, parseFloat(event.target.value) || 0); // Update cache
        this.performUpdate();
    }
}