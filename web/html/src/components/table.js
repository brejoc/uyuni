"use strict";

var React = require("react")
var StatePersistedMixin = require("./util").StatePersistedMixin

var Table = React.createClass({
  mixins: [StatePersistedMixin],

  propTypes: {
    headers: React.PropTypes.arrayOf(React.PropTypes.node).isRequired,
    rows: React.PropTypes.arrayOf(React.PropTypes.node).isRequired,
    rowFilter: React.PropTypes.func, // (row, searchString) -> boolean
    filterPlaceholder: React.PropTypes.string,
    rowComparator: React.PropTypes.func, // (row1, row2, sortColumnIndex, ascending) -> -1/0/+1
    sortableColumnIndexes: React.PropTypes.arrayOf(React.PropTypes.number), // required with rowComparator
  },

  getInitialState: function() {
    return {
      currentPage: 1,
      itemsPerPage: 15,
      filterText: "",
      sortColumnIndex: 0,
      sortAscending: true
    };
  },

  componentWillReceiveProps: function(nextProps) {
    var lastPage = Math.ceil(nextProps.rows.length / this.state.itemsPerPage);
    if (this.state.currentPage > lastPage) {
      this.setState({currentPage: lastPage});
    }
  },

  onSortColumnIndexChange: function(sortColumnIndex) {
    this.setState({
      sortColumnIndex: sortColumnIndex,
      sortAscending: this.state.sortColumnIndex != sortColumnIndex || !this.state.sortAscending
    });
  },

  getProcessedRows: function() {
    const filter = this.props.rowFilter ?
      (row) => this.props.rowFilter(row, this.props.filterText) :
      (row) => true
    ;

    const comparator = this.props.rowComparator ?
      (a, b) => this.props.rowComparator(a, b, this.state.sortColumnIndex, this.state.sortAscending) :
      (a, b) => 0
    ;

    return this.props.rows.filter(filter).sort(comparator);
  },

  lastPage: function(rows, itemsPerPage) {
    var lastPage = Math.ceil(rows.length / itemsPerPage);
    if (lastPage == 0) {
      return 1;
    }
    return lastPage;
  },

  goToPage:function(page) {
    this.setState({currentPage: page});
  },

  onItemsPerPageChange: function(itemsPerPage) {
    this.setState({itemsPerPage: itemsPerPage});
    var lastPage = this.lastPage(this.getProcessedRows(), itemsPerPage);
    if (this.state.currentPage > lastPage) {
      this.setState({currentPage: lastPage });
    }
  },

  onSearchFieldChange: function(searchValue) {
    this.setState({filterText: searchValue});
    var lastPage =  this.lastPage(this.getProcessedRows(), this.state.itemsPerPage);
    if (this.state.currentPage > lastPage) {
      this.setState({currentPage: lastPage});
    }
  },

  render: function() {
    var rows = this.getProcessedRows();
    var itemsPerPage = this.state.itemsPerPage;
    var itemCount = rows.length;
    var lastPage = this.lastPage(rows, itemsPerPage);
    var currentPage = this.state.currentPage;

    var firstItemIndex = (currentPage - 1) * itemsPerPage;

    var fromItem = itemCount > 0 ? firstItemIndex +1 : 0;
    var toItem = firstItemIndex + itemsPerPage <= itemCount ? firstItemIndex + itemsPerPage : itemCount;

    var pagination;
    if (lastPage > 1) {
      pagination = (
        <div className="spacewalk-list-pagination">
          <div className="spacewalk-list-pagination-btns btn-group">
            <PaginationButton onClick={() => this.goToPage(1)} toPage={1} disabled={currentPage == 1} text={t("First")} />
            <PaginationButton onClick={() => this.goToPage(currentPage -1)} disabled={currentPage == 1} text={t("Prev")} />
            <PaginationButton onClick={() => this.goToPage(currentPage +1)} disabled={currentPage == lastPage} text={t("Next")} />
            <PaginationButton onClick={() => this.goToPage(lastPage)} disabled={currentPage == lastPage} text={t("Last")} />
          </div>
        </div>
      );
    }

    var searchField;
    if (this.props.rowFilter) {
      searchField = (
        <SearchField
          onChange={this.onSearchFieldChange}
          defaultValue={this.state.filterText}
          placeholder={this.props.filterPlaceholder}
        />
      );
    }

    return (
      <div className="spacewalk-list">
        <div className="panel panel-default">
          <div className="panel-heading">
            <div className="spacewalk-list-head-addons">
              <div className="spacewalk-list-filter table-search-wrapper">
                {searchField} {t("Items {0} - {1} of {2}", fromItem, toItem, itemCount)}
              </div>
              <div className="spacewalk-list-head-addons-extra table-items-per-page-wrapper">
                <PageSelector className="display-number"
                  options={[5,10,15,25,50,100,250,500]}
                  currentValue={itemsPerPage}
                  onChange={this.onItemsPerPageChange}
                /> {t("items per page")}
              </div>
            </div>
          </div>
          <div className="table-responsive">
            <table className="table table-striped">
              <TableHeader
                content={
                  this.props.headers.map((header, index) => {
                    var className;
                    if (index == this.state.sortColumnIndex) {
                      className = (this.state.sortAscending ? "asc" : "desc") + "Sort";
                    }
                    return (
                        (this.props.sortableColumnIndexes &&
                          this.props.sortableColumnIndexes.filter((element) => element == index).length > 0) ?
                        <TableHeaderCellOrder className={className} content={header}
                          orderBy={() => this.onSortColumnIndexChange(index)} /> :
                        <TableHeaderCell className={className} content={header} />
                    );
                  })}
              />
              <tbody className="table-content">
                {rows
                  .filter((element, i) => i >= firstItemIndex && i < firstItemIndex + itemsPerPage)
                }
                </tbody>
            </table>
          </div>
          <div className="panel-footer">
            <div className="spacewalk-list-bottom-addons">
              <div className="table-page-information">{t("Page {0} of {1}", currentPage, lastPage)}</div>
              {pagination}
            </div>
          </div>
        </div>
      </div>
    );
  }
});

var TableRow = (props) => <tr className={props.className}>{props.columns}</tr>;

var TableCell = (props) => <td>{props.content}</td>;

var PaginationButton = (props) =>
  <button type="button" className="btn btn-default"
    disabled={props.disabled} onClick={props.onClick}>
    {props.text}
  </button>
;

var PageSelector = (props) =>
  <select className={props.className}
    defaultValue={props.currentValue}
    onChange={(e) => props.onChange(parseInt(e.target.value))}>
      {props.options.map((o) => <option value={o}>{o}</option>)}
  </select>
;

var TableHeader = (props) => <thead><tr>{props.content}</tr></thead>;

var TableHeaderCellOrder = (props) =>
  <th className={props.className}>
    <a className="orderBy" onClick={props.orderBy}>{props.content}</a>
  </th>
;

var TableHeaderCell = (props) => <th className={props.className}>{props.content}</th>;

var SearchField = (props) =>
  <input className="form-control table-input-search"
    value={props.defaultValue}
    placeholder={props.placeholder}
    type="text"
    onChange={(e) => props.onChange(e.target.value)}
  />
;

module.exports = {
    Table : Table,
    TableCell : TableCell,
    TableRow : TableRow
}
