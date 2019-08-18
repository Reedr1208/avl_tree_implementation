#avl imp
import random
import sys
import time
import numpy as np




class Avl:
	def __init__(self, values=[]):
		"""
		ATTRIBUTES
			tree- A nested array data structure containing the AVL tree
				format: [[value, left child index, right child index, parent index, node height (leaf=1), balance factor], [elemt2], [elemt3], etc]
				tree[i][0]= node value
				tree[i][1]= left child index
				tree[i][2]= right child index
				tree[i][3]= parent index
				tree[i][4]= node height
				tree[i][5]= node balance factor
			root_index- The array index of the root element
			free_spots- an array of indecies of AVL elements which have been deleted and can be re-assigned

		METHODS
			find- Search for node of provided value
			update_heights- Update node heights of provided node and all of its ancestors
			rotate- Rotate sub-tree at provided index to rebalance tree and recover AVL property 
			insert- insert new node of given value (duplicates are allowed)
			next- return the index of the next node in ascending order
			sort_tree- return a sorted array of all element values (ascending)
			delete_by_index- delete the node at the provided index
			delete_by_value- delete the first node found with provided value

		"""

		self.tree=[]
		self.root_index=None

		self.free_spots=[]

		#build initial AVL tree using provided values
		for val in values:
			self.insert(val)

	def find(self, value, search_index=None, parent_index=None, ignore_matches=False, level=0):
		"""
		searches for a node of provided value
		
		INPUT:
			value= the value of the node to search
			search_index= the index of the node to start search at. First initialied to root node index if a root exists
			parent_index= The parent index of the node being searched. This is used for determining where to put a node
			ignore_matches
				if true, function will return the index where the next elemnt should be placed
				if false, the function will terminate if the search value is found and return its info

		RETURNS:
		tuple (bool, index, parent index)
			bool
				True: Node was found
				False: Node was not found
			index:
				If found, returns the index of the searched note in the tree
				If not found, returns the index that the node ought to have (assuming all spots are filled)
			parent index: The parent index of node which was found or of the node which would be created from the seached value
		"""
		
		#Initialize search index to root node if it exists, otherwise, leave as None and return result
		if search_index==None:
			search_index=self.root_index
			if search_index==None:
				return (False, len(self.tree), parent_index)

		current_value= self.tree[search_index][0]
		left_child_index=self.tree[search_index][1]
		right_child_index= self.tree[search_index][2]
		parent_index=self.tree[search_index][3]


		#return result if match is found (only if ignore matches is set to false)
		if current_value==value and ignore_matches==False:
			return (True, search_index, parent_index)
		
		#if searched value is greater than current node, search the right child
		elif value >= current_value:
			#does a left child exist?
			if right_child_index==None:
				return (False, len(self.tree), search_index)
			else:
				return self.find(value, search_index=right_child_index, parent_index=search_index, ignore_matches=ignore_matches, level=level+1)

		#is searched value less than current node?
		elif value < current_value:

			#does a left child exist?
			if left_child_index==None:
				return (False, len(self.tree), search_index)
			
			#search the left child
			else:
				return self.find(value, search_index=left_child_index, parent_index=search_index, ignore_matches=ignore_matches, level=level+1)


	def update_heights(self, node_index):
		"""
		-Recursively updates the height & balance factor of node and its ancestors, rotating where needed
		-If rotation is needed, then function will back-track to first properly update the heights of children affected by the rotation
		-Height is measured relative to the deepest descendent leaf (leaves have height one, root has largest height)
		-Balance Factor is the difference between height of right chld and left child
		-Function will start with provided node and follow the tree to the root, updating the height of each node along the path
		
		INPUT:
			node_index= the index of the node to start updating at
		
		RETURNS:
			Function returns nothing
		"""
		#Node index will be set to none after root node has height updated
		if node_index==None:
			return

		if self.tree[node_index][1]==None:
			left_child_height=0
		else:
			left_child_height= self.tree[self.tree[node_index][1]][4]

		if self.tree[node_index][2]==None:
			right_child_height=0
		else:
			right_child_height= self.tree[self.tree[node_index][2]][4]
		
		#update node height and balance factor
		self.tree[node_index][4]= max(left_child_height, right_child_height)+1
		self.tree[node_index][5]= right_child_height-left_child_height

		#after updating current node's height, update the height of the parent
		next_index= self.tree[node_index][3]
		
		#Rotations must recover AVL property if balance factor magnitude exceeds 1
		if abs(self.tree[node_index][5])>=2:
			next_index= self.rotate(node_index)

		#update height of next node (parent)
		self.update_heights(next_index)



	def rotate(self, node_index):
		"""
		Function uses rotations to recover AVL property when a nodes balance factor exceeds magnitude of 1
		
		INPUT:
			node_index= Index of node with invalid balance factor

		RETURNS:
			return_val= The index of the node which should be updated next
				possibility 1- The parent of the current node
				possibility 2- The deepest child affected by a rotation
		"""

		balance_factor = self.tree[node_index][5]
		
		#The same code is used for left and right rotations
		#The mod value will adjust indexing such that it is consistent with the required rotation type (right or left)
		if balance_factor<0:
			#right rotation (left side is too big)
			mod=0
		else:
			#left rotation (right side is too big)
			mod=1

		#node's child on the heavy side
		sub_node_index= self.tree[node_index][1+mod]

		#declare an initial return value, and only modify if certian logic branches are followed
		return_val= self.tree[node_index][1+mod]

		#balance factor of child on heavy side
		sub_balance_factor= self.tree[sub_node_index][5]

		#two opposite rotations are needed if current node and node's heavy-side child have opposite balance factors (negative product)
		#if this is the case, perform the following rotation first
		if balance_factor*sub_balance_factor<0:
			
			#this additional rotation will require the height update to start with the heavy-side child node
			return_val= sub_node_index

			grand_node_index= self.tree[sub_node_index][2-mod]

			#If there are inner children of grandchild node, they will need to switch parents with the rotation
			inner_node_index=self.tree[grand_node_index][1+mod]
			if inner_node_index!=None:
				#reassign inner node
				self.tree[inner_node_index][3]=sub_node_index
				self.tree[sub_node_index][2-mod]=inner_node_index
			else:
				self.tree[sub_node_index][2-mod]=None
			

			#move grand node to sub node position and build relationship with parent node
			self.tree[grand_node_index][3]= node_index
			self.tree[node_index][1+mod]= grand_node_index

			#move sub node down a level and form relationship with grand node
			self.tree[sub_node_index][3]= grand_node_index
			self.tree[grand_node_index][1+mod]= sub_node_index
		
		
		#The following rotation is neccesary for all cases
		sub_node_index= self.tree[node_index][1+mod]
		grand_node_index= self.tree[sub_node_index][1+mod]

		inner_node_index=self.tree[sub_node_index][2-mod]
		if inner_node_index!=None:
			#Assign inner node to new parent if one exists
			self.tree[inner_node_index][3]=node_index
			self.tree[node_index][1+mod]=inner_node_index
		else:
			self.tree[node_index][1+mod]=None


		self.tree[sub_node_index][2-mod]=node_index
		self.tree[sub_node_index][3]=self.tree[node_index][3]
		
		parent_node_index=self.tree[sub_node_index][3]
		
		#if sub-node as moved into the root node's position, then update root node of AVL tree to reference the new root
		#Otherwise, follow standard logic to update relationships among nodes
		if parent_node_index==None:
			self.root_index=sub_node_index
		else:
			if self.tree[parent_node_index][1]==node_index:
				self.tree[parent_node_index][1]= sub_node_index
			else:
				self.tree[parent_node_index][2]= sub_node_index


		self.tree[node_index][3]=sub_node_index

		#Update heights and balance factors of main node since this will be missed by the update_heights function
		if self.tree[node_index][1]==None:
			lc=0
		else:
			lc= self.tree[self.tree[node_index][1]][4]
		if self.tree[node_index][2]==None:
			rc=0
		else:
			rc= self.tree[self.tree[node_index][2]][4]

		self.tree[node_index][4]= max(lc, rc)+1
		self.tree[node_index][5]=rc-lc
					
		return return_val



	def insert(self, value):
		"""
		Function will insert a node into the AVL tree. Duplicates are allowed
		Function will re-assign array positions where old nodes were deleted. Otherwise, it will append a new element to tree array
		Function will update heights and balance factors automatically and perform rotations when needed
		This funciton is repeatedly called in order to build teh initial AVL tree

		INPUT:
			value- the value associated with node to be added
		RETURNS:
			Returns nothing
		"""
		#new_node= The array index and parent of the node to be added
		new_node= self.find(value, ignore_matches=True)
		new_node_index= new_node[1]
		new_node_parent_index= new_node[2]

		#If there are any free spots in the array created by deleting nodes, reassign these positions instead
		if len(self.free_spots)>0:
			new_node_index=self.free_spots.pop()
			self.tree[new_node_index]=[value, None, None, new_node_parent_index, 1, 0]
		else:
			self.tree.append([value, None, None, new_node_parent_index, 1, 0])

		#determine whether new node is the left or right child 
		#update the parent to point to new node
		#if new node is the root, do nothing
		if new_node_parent_index!=None:
			if value>=self.tree[new_node_parent_index][0]:
				self.tree[new_node_parent_index][2]= new_node_index
			else:
				self.tree[new_node_parent_index][1]= new_node_index
		else:
			self.root_index=new_node_index

		#update node heights starting with the parent of the node which was just added
		self.update_heights(new_node_parent_index)

	def next(self, starting_index):
		"""
		Find the index of the next node in ascending order
		This method is called repeatedly when returning a sorted AVL tree

		INPUT:
			starting_index= The index of the node for which the next node's index should be returned
		RETURNS:
			next_index- The index of next node in ascending order
		"""
		if self.tree[starting_index][2]!=None:

			next_index= self.tree[starting_index][2]
			while self.tree[next_index][1]!=None:
				next_index=self.tree[next_index][1]
			return next_index

		else:
			parent_index=self.tree[starting_index][3]
			while parent_index!=None:
				if self.tree[parent_index][1]==starting_index:
					return parent_index
				starting_index=parent_index
				parent_index= self.tree[parent_index][3]

		return None

	def sort_tree(self):
		#Funciton calls the 'next' method repeatedly to build a sorted array from AVL tree
		
		sorted_values=[]

		#travel from root to lowest valued node
		current_index= self.root_index
		if current_index==None:
			return []
		while self.tree[current_index][1]!=None:
			current_index=self.tree[current_index][1]
		
		while current_index!=None:
			sorted_values.append(self.tree[current_index][0])
			current_index= self.next(current_index)

		return sorted_values

	def delete_by_index(self, node_index):
		"""
		Delete a node in the AVL tree by its index
		Funciton build to handle three cases
			Case 1- Node to be deleted has no children
			Case 2- Node has 1 child. Requires one node to be promoted
			Case 3- Node has 2 children. This case requires more complext re-arrangement
		INPUT:
			node_index= index of node to be deleted
		RETURNS:
			Nothing
		"""

		#CASE 1- no children
		if self.tree[node_index][1]==self.tree[node_index][2]==None:
			#define parent and delete node
			parent_index=self.tree[node_index][3]
			self.tree[node_index]=None
			self.free_spots.append(node_index)
			
			#if node was root, null out the rot index
			if parent_index==None:
				self.root_index=None
			#otherwise update the parent to reference None
			else: 
				if self.tree[parent_index][1]==node_index:
					self.tree[parent_index][1]=None
				else:
					self.tree[parent_index][2]=None
				self.update_heights(parent_index)
				return

		#CASE 2- 1 child
		elif any([i!=None for i in [self.tree[node_index][1], self.tree[node_index][2]]]) and None in [self.tree[node_index][1], self.tree[node_index][2]]:
			
			parent_index= self.tree[node_index][3]

			#find index of non-null child
			if self.tree[node_index][1]!=None:
				child_index=self.tree[node_index][1]
			else:
				child_index=self.tree[node_index][2]

			#delete node and open position
			self.tree[node_index]=None
			self.free_spots.append(node_index)

			self.tree[child_index][3]=parent_index

			#re-assign root if deleted node was root
			if parent_index==None:
				self.root_index=child_index
			#otherwise, update deleted nodes parent to reference promoted node
			elif self.tree[parent_index][1]==node_index:
				self.tree[parent_index][1]=child_index
			else:
				self.tree[parent_index][2]=child_index

			self.update_heights(child_index)
			return


		#CASE 3- two children
		#Delete node
		#Promote the next node to take its position
		#Promote the right child of the recently promoted node to take its position
		elif self.tree[node_index][1]!=None and self.tree[node_index][2]!=None:
			promoted_next= self.next(node_index)
			parent_index= self.tree[node_index][3]
			left_child= self.tree[node_index][1]
			right_child=self.tree[node_index][2]

			#if promoted node is right child of deleted node
			if promoted_next==right_child:
				self.tree[promoted_next][1]= left_child
				self.tree[left_child][3]=promoted_next
				self.tree[promoted_next][3]=parent_index

				if parent_index==None:
					self.root_index=promoted_next
				elif self.tree[parent_index][1]==node_index:
					self.tree[parent_index][1]=promoted_next
				else:
					self.tree[parent_index][2]=promoted_next

				self.tree[node_index]=None
				self.free_spots.append(node_index)
				self.update_heights(promoted_next)

			#if promoted node is not the right child of the deleted node
			else:
				#update index= The node at which to start height updates with. This will depend on the logical path followed
				update_index=None
				pn_parent_index= self.tree[promoted_next][3]
				pn_right_child= self.tree[promoted_next][2]

				#promoted next node does not have ANY children (if it had left child, then that left child would be the next index)
				if pn_right_child==None:
					self.tree[pn_parent_index][1]=None
					update_index=pn_parent_index

				#if promoted next does have a right child
				else:
					self.tree[pn_right_child][3]= pn_parent_index
					self.tree[pn_parent_index][1]= pn_right_child
					update_index= pn_right_child

				#Update inter-node relationships
				self.tree[promoted_next][3]=parent_index
				self.tree[promoted_next][1]=left_child
				self.tree[promoted_next][2]=right_child

				#update family to point to promoted next
				if parent_index==None:
					self.root_index=promoted_next
				elif self.tree[parent_index][1]==node_index:
					self.tree[parent_index][1]=promoted_next
				else:
					self.tree[parent_index][2]=promoted_next

				self.tree[left_child][3]=promoted_next
				self.tree[right_child][3]=promoted_next
				self.tree[node_index]=None
				self.free_spots.append(node_index)

				#Update heights and balance factors starting with assigned update_index
				self.update_heights(update_index)


	def delete_by_value(self, value):
		#Find the index of a node with the provided value
		result= self.find(value)
		if result[0]:
			self.delete_by_index(result[1])


#if user runs this file directly, the sample case below will be executed
if __name__ == "__main__":

	max_num= 10**4
	num_nodes= 10**4
	num_deletions= 2*10**3
	num_insertions=3*10**3



	sample_input= [random.randint(-1*max_num, max_num) for i in range(num_nodes)]
	delete_vals= np.random.choice(sample_input, num_deletions, replace=False)
	insert_vals=[random.randint(-1*max_num, max_num) for x in range(num_insertions)]
	py_list=list(sample_input)

	start=time.time()
	avl=Avl(sample_input)
	end=time.time()
	print('\nTime to build AVL tree of {} elements: {}s'.format(len(avl.tree), round((end-start), 2)))

	start=time.time()
	for i in delete_vals:
		avl.delete_by_value(i)
	end= time.time()
	print('\nTime to delete {} values from AVL tree: {}s'.format(len(delete_vals), round((end-start), 2)))

	start=time.time()
	for i in insert_vals:
		avl.insert(i)
	end= time.time()
	print('\nTime to insert {} values into AVL tree: {}s'.format(len(insert_vals), round((end-start), 2)))

	for i in delete_vals:
		try:
			py_list.remove(i)
		except:
			pass
	py_list= py_list+insert_vals

	py_list.sort()

	start=time.time()
	sorted_avl= avl.sort_tree()
	end= time.time()
	print('\nTime to sort AVL tree: {}s'.format(round((end-start), 2)))

	test_result='FAILED'
	if py_list==sorted_avl:
		test_result='PASSED'

	print('\nTest- Comparing sorted list with sorted AVL tree: {}'.format(test_result))

	print('\nUpdated tree size: {}'.format(len(avl.tree)-len(avl.free_spots)))

	print('\nTree height: {}'.format(avl.tree[avl.root_index][4]))


