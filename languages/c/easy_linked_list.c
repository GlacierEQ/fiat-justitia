/**
 * C — Easy Example: Linked List with Manual Memory Management
 * What: Singly-linked list with malloc/free lifecycle.
 * Where: Embedded systems, kernel modules, bare-metal firmware.
 * When: Maximum control over memory layout and hardware registers.
 * Why: The lingua franca of systems programming — runs everywhere.
 * How: Direct pointer arithmetic and manual heap management.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct Node {
    int value;
    struct Node* next;
} Node;

typedef struct LinkedList {
    Node* head;
    size_t length;
} LinkedList;

LinkedList* list_create(void) {
    LinkedList* list = (LinkedList*)malloc(sizeof(LinkedList));
    if (!list) return NULL;
    list->head = NULL;
    list->length = 0;
    return list;
}

int list_push(LinkedList* list, int value) {
    Node* node = (Node*)malloc(sizeof(Node));
    if (!node) return -1;
    node->value = value;
    node->next = list->head;
    list->head = node;
    list->length++;
    return 0;
}

int list_pop(LinkedList* list) {
    if (!list->head) return -1;
    Node* old = list->head;
    int value = old->value;
    list->head = old->next;
    free(old);
    list->length--;
    return value;
}

void list_print(const LinkedList* list) {
    printf("[");
    for (Node* n = list->head; n; n = n->next) {
        printf("%d%s", n->value, n->next ? ", " : "");
    }
    printf("] (len=%zu)\n", list->length);
}

void list_destroy(LinkedList* list) {
    while (list->head) {
        list_pop(list);
    }
    free(list);
}

int main(void) {
    LinkedList* list = list_create();
    for (int i = 1; i <= 10; i++) {
        list_push(list, i * i);
    }
    printf("Stack (LIFO): ");
    list_print(list);

    printf("Popped: %d\n", list_pop(list));
    printf("After pop: ");
    list_print(list);

    list_destroy(list);
    printf("Memory freed. No leaks.\n");
    return 0;
}
